import asyncio
import json
from types import SimpleNamespace
from typing import cast

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, SystemMessage, ToolMessage

from apps.civic_assistant.mcp.workflow.errors import CivicAssistantGraphError
from apps.civic_assistant.mcp.workflow.graph import build_civic_assistant_graph

from .conftest import FakeFinalModel, make_organization_payload, make_organization_tool_call


async def collect_events(graph, message: str):
    return [event async for event in graph.astream({"message": message}, stream_mode="custom")]


def build_graph(model, mcp_client, prompts):
    return build_civic_assistant_graph(
        model=cast(BaseChatModel, model),
        mcp_client=mcp_client,
        prompts=prompts,
    )


def configure_mcp_client(mcp_client, payloads):
    async def call_tool(name, arguments):
        return SimpleNamespace(
            structured_content=payloads[arguments["slug"]],
            is_error=payloads[arguments["slug"]] is None,
        )

    mcp_client.call_tool.side_effect = call_tool


class TestCivicAssistantGraph:
    def test_no_tool_path_only_streams_final_deltas(self, mcp_client, civic_prompt_snapshot):
        model = FakeFinalModel(
            AIMessage(content="private selection reasoning"),
            [
                AIMessageChunk(content=[{"type": "reasoning", "reasoning": "private final reasoning"}]),
                AIMessageChunk(content="public answer"),
            ],
        )
        graph = build_graph(
            model=model,
            mcp_client=mcp_client,
            prompts=civic_prompt_snapshot,
        )

        events = asyncio.run(collect_events(graph, "What is civic participation?"))

        assert events == [{"type": "delta", "text": "public answer"}]
        mcp_client.call_tool.assert_not_awaited()
        assert model.calls == [
            [
                SystemMessage(content=civic_prompt_snapshot.answer),
                HumanMessage(content="What is civic participation?"),
            ]
        ]
        assert all("private" not in str(message.content) for message in model.calls[0])

    def test_single_lookup_reaches_final_generation_with_bounded_evidence(self, mcp_client, civic_prompt_snapshot):
        configure_mcp_client(mcp_client, {"doh": make_organization_payload("doh")})
        model = FakeFinalModel(
            AIMessage(
                content="private selection reasoning",
                tool_calls=[make_organization_tool_call("doh", "call-doh")],
            ),
            [AIMessageChunk(content="final answer")],
        )
        graph = build_graph(
            model=model,
            mcp_client=mcp_client,
            prompts=civic_prompt_snapshot,
        )

        events = asyncio.run(collect_events(graph, "Tell me about DOH."))

        assert events == [{"type": "delta", "text": "final answer"}]
        mcp_client.call_tool.assert_awaited_once_with("get_organization_overview", {"slug": "doh"})
        assert model.calls[0][0] == SystemMessage(content=civic_prompt_snapshot.answer)
        assert model.calls[0][1] == HumanMessage(content="Tell me about DOH.")
        selection = model.calls[0][2]
        assert isinstance(selection, AIMessage)
        assert selection.content == ""
        assert selection.tool_calls[0]["id"] == "call-doh"
        evidence = model.calls[0][3]
        assert isinstance(evidence, ToolMessage)
        assert isinstance(evidence.content, str)
        assert json.loads(evidence.content) == {
            "status": "ok",
            "organization": make_organization_payload("doh"),
        }

    def test_multi_organization_lookup_preserves_order_and_pairing(self, mcp_client, civic_prompt_snapshot):
        slugs = ("doh", "deped", "dilg")
        configure_mcp_client(mcp_client, {slug: make_organization_payload(slug) for slug in slugs})
        model = FakeFinalModel(
            AIMessage(
                content="private planning",
                tool_calls=[make_organization_tool_call(slug, f"call-{slug}") for slug in slugs],
            ),
            [AIMessageChunk(content="comparison")],
        )
        graph = build_graph(
            model=model,
            mcp_client=mcp_client,
            prompts=civic_prompt_snapshot,
        )

        events = asyncio.run(collect_events(graph, "Compare DOH, DepEd, and DILG."))

        assert events == [{"type": "delta", "text": "comparison"}]
        assert [call.args[1]["slug"] for call in mcp_client.call_tool.await_args_list] == list(slugs)
        final_messages = model.calls[0]
        tool_messages = [message for message in final_messages[3:] if isinstance(message, ToolMessage)]
        assert [message.tool_call_id for message in tool_messages] == [
            "call-doh",
            "call-deped",
            "call-dilg",
        ]
        assert all(message.content != "private planning" for message in final_messages)

    def test_partial_unavailable_result_still_reaches_final_model(self, mcp_client, civic_prompt_snapshot):
        configure_mcp_client(mcp_client, {"doh": make_organization_payload("doh"), "deped": None})
        model = FakeFinalModel(
            AIMessage(
                content="private planning",
                tool_calls=[
                    make_organization_tool_call("doh", "call-doh"),
                    make_organization_tool_call("deped", "call-deped"),
                ],
            ),
            [AIMessageChunk(content="answer with partial evidence")],
        )
        graph = build_graph(
            model=model,
            mcp_client=mcp_client,
            prompts=civic_prompt_snapshot,
        )

        events = asyncio.run(collect_events(graph, "Compare DOH and DepEd."))

        assert events == [{"type": "delta", "text": "answer with partial evidence"}]
        assert len(model.calls[0]) == 5
        available_evidence = model.calls[0][3]
        assert isinstance(available_evidence, ToolMessage)
        assert available_evidence.tool_call_id == "call-doh"
        unavailable_evidence = model.calls[0][4]
        assert isinstance(unavailable_evidence, ToolMessage)
        assert unavailable_evidence.content == '{"status":"unavailable"}'
        assert "internal" not in str(unavailable_evidence.content)

    def test_invalid_selection_fails_before_mcp_invocation(self, mcp_client, civic_prompt_snapshot):
        model = FakeFinalModel(
            AIMessage(
                content="private planning",
                tool_calls=[{"name": "unsupported", "args": {}, "id": "call-1"}],
            ),
            [AIMessageChunk(content="should not be generated")],
        )
        graph = build_graph(
            model=model,
            mcp_client=mcp_client,
            prompts=civic_prompt_snapshot,
        )

        with pytest.raises(CivicAssistantGraphError, match="unsupported tool"):
            asyncio.run(collect_events(graph, "Use an unsupported capability."))

        mcp_client.call_tool.assert_not_awaited()
        assert model.calls == []

    def test_binds_selection_model_for_parallel_tool_calls(self, mcp_client, civic_prompt_snapshot):
        model = FakeFinalModel(AIMessage(content=""), [AIMessageChunk(content="answer")])

        build_graph(
            model=model,
            mcp_client=mcp_client,
            prompts=civic_prompt_snapshot,
        )

        assert [tool.name for tool in model.bound_tools] == ["get_organization_overview"]
        assert model.bind_kwargs == {"strict": True, "parallel_tool_calls": True}
