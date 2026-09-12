import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, SystemMessage, ToolMessage

from apps.civic_assistant.mcp.workflow.constants import ANSWER_NODE, LOOKUP_NODE
from apps.civic_assistant.mcp.workflow.errors import CivicAssistantGraphError
from apps.civic_assistant.mcp.workflow.nodes import (
    MAX_TOOL_CALLS_PER_REQUEST,
    build_final_messages,
    choose_after_selection,
    lookup,
    public_text,
    select_tool,
)


class TestSelectTool:
    def test_discards_private_prose_when_no_tools_are_selected(self, civic_prompt_snapshot):
        selecting_model = Mock()
        selecting_model.ainvoke = AsyncMock(return_value=AIMessage(content="private reasoning"))

        result = asyncio.run(
            select_tool(
                {"message": "Who leads the health department?"},
                selecting_model=selecting_model,
                prompts=civic_prompt_snapshot,
            )
        )

        selection = result.get("selection")
        assert selection is not None
        assert selection.content == ""
        assert selection.tool_calls == []

    @pytest.mark.parametrize(
        ("response", "message"),
        [
            (
                AIMessage(content="", tool_calls=[{"name": "unsupported", "args": {}, "id": "call-1"}]),
                "unsupported tool",
            ),
            (
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "get_organization_overview",
                            "args": {"slug": "has spaces"},
                            "id": "call-1",
                        }
                    ],
                ),
                "invalid tool arguments",
            ),
            (
                AIMessage(
                    content="",
                    tool_calls=[{"name": "get_organization_overview", "args": {"slug": "doh"}, "id": None}],
                ),
                "without an ID",
            ),
            (
                AIMessage(
                    content="",
                    tool_calls=[{"name": "get_organization_overview", "args": {"slug": "doh"}, "id": " "}],
                ),
                "without an ID",
            ),
            (
                AIMessage(
                    content="",
                    tool_calls=[
                        {"name": "get_organization_overview", "args": {"slug": "doh"}, "id": "duplicate"},
                        {"name": "get_organization_overview", "args": {"slug": "deped"}, "id": "duplicate"},
                    ],
                ),
                "duplicate",
            ),
            (
                AIMessage(
                    content="",
                    tool_calls=[
                        {"name": "get_organization_overview", "args": {"slug": "doh"}, "id": f"call-{i}"}
                        for i in range(MAX_TOOL_CALLS_PER_REQUEST + 1)
                    ],
                ),
                "exceeded",
            ),
            (
                AIMessage(
                    content="",
                    invalid_tool_calls=[
                        {"name": "get_organization_overview", "args": "{", "id": "call-1", "error": "invalid"}
                    ],
                ),
                "invalid tool call",
            ),
        ],
    )
    def test_rejects_unsafe_selection_responses(self, response, message, civic_prompt_snapshot):
        selecting_model = Mock()
        selecting_model.ainvoke = AsyncMock(return_value=response)

        with pytest.raises(CivicAssistantGraphError, match=message):
            asyncio.run(
                select_tool(
                    {"message": "Find organizations."},
                    selecting_model=selecting_model,
                    prompts=civic_prompt_snapshot,
                )
            )

    def test_preserves_multiple_valid_organization_lookups(self, civic_prompt_snapshot):
        response = AIMessage(
            content="private planning",
            tool_calls=[
                {"name": "get_organization_overview", "args": {"slug": slug}, "id": f"call-{slug}"}
                for slug in ("doh", "deped", "dilg")
            ],
        )
        selecting_model = Mock()
        selecting_model.ainvoke = AsyncMock(return_value=response)

        result = asyncio.run(
            select_tool(
                {"message": "Compare these organizations."},
                selecting_model=selecting_model,
                prompts=civic_prompt_snapshot,
            )
        )

        selection = result.get("selection")
        assert selection is not None
        assert selection.content == ""
        assert [call["args"]["slug"] for call in selection.tool_calls] == ["doh", "deped", "dilg"]
        assert [call["id"] for call in selection.tool_calls] == ["call-doh", "call-deped", "call-dilg"]

    def test_rejects_a_non_ai_message_response(self, civic_prompt_snapshot):
        selecting_model = Mock()
        selecting_model.ainvoke = AsyncMock(return_value=HumanMessage(content="not an AI response"))

        with pytest.raises(CivicAssistantGraphError, match="invalid response"):
            asyncio.run(
                select_tool(
                    {"message": "Find an organization."},
                    selecting_model=selecting_model,
                    prompts=civic_prompt_snapshot,
                )
            )


class TestRoutingAndLookup:
    def test_routes_no_tool_calls_to_answer(self):
        assert choose_after_selection({"message": "Hello", "selection": AIMessage(content="")}) == ANSWER_NODE

    def test_routes_tool_calls_to_lookup(self, organization_tool_call):
        selection = AIMessage(content="", tool_calls=[organization_tool_call("doh", "call-doh")])

        assert choose_after_selection({"message": "Overview", "selection": selection}) == LOOKUP_NODE

    def test_requires_selection_for_routing(self):
        with pytest.raises(CivicAssistantGraphError, match="did not produce"):
            choose_after_selection({"message": "Hello"})

    def test_executes_all_selected_calls_in_order(self, organization_tool_call):
        selection = AIMessage(
            content="",
            tool_calls=[organization_tool_call(slug, f"call-{slug}") for slug in ("doh", "deped", "dilg")],
        )
        overview_tool = Mock()
        overview_tool.ainvoke = AsyncMock(side_effect=["doh evidence", "deped evidence", "dilg evidence"])

        result = asyncio.run(
            lookup(
                {"message": "Compare", "selection": selection},
                overview_tool=overview_tool,
            )
        )

        tool_messages = result.get("tool_messages")
        assert tool_messages is not None
        assert [message.content for message in tool_messages] == [
            "doh evidence",
            "deped evidence",
            "dilg evidence",
        ]
        assert [message.tool_call_id for message in tool_messages] == [
            "call-doh",
            "call-deped",
            "call-dilg",
        ]
        assert [call.args[0] for call in overview_tool.ainvoke.await_args_list] == [
            {"slug": "doh"},
            {"slug": "deped"},
            {"slug": "dilg"},
        ]

    @pytest.mark.parametrize(
        "state",
        [
            {"message": "Compare"},
            {"message": "Compare", "selection": AIMessage(content="")},
        ],
    )
    def test_requires_non_empty_selection_for_lookup(self, state):
        with pytest.raises(CivicAssistantGraphError, match="validated tool calls"):
            asyncio.run(lookup(state, overview_tool=Mock()))

    def test_rejects_non_string_evidence(self, organization_tool_call):
        selection = AIMessage(content="", tool_calls=[organization_tool_call("doh", "call-doh")])
        overview_tool = Mock()
        overview_tool.ainvoke = AsyncMock(return_value={"status": "ok"})

        with pytest.raises(CivicAssistantGraphError, match="invalid evidence"):
            asyncio.run(lookup({"message": "Overview", "selection": selection}, overview_tool=overview_tool))


class TestFinalMessages:
    def test_no_tool_path_contains_only_final_prompt_and_human_message(self, civic_prompt_snapshot):
        messages = build_final_messages(
            state={"message": "What is civic participation?", "selection": AIMessage(content="")},
            prompts=civic_prompt_snapshot,
        )

        assert messages == [
            SystemMessage(content=civic_prompt_snapshot.answer),
            HumanMessage(content="What is civic participation?"),
        ]

    def test_tool_path_contains_sanitized_selection_and_all_tool_messages(
        self, civic_prompt_snapshot, organization_tool_call
    ):
        selection = AIMessage(content="", tool_calls=[organization_tool_call("doh", "call-doh")])
        tool_messages = [
            ToolMessage(content="doh evidence", name="get_organization_overview", tool_call_id="call-doh"),
            ToolMessage(content="deped evidence", name="get_organization_overview", tool_call_id="call-deped"),
        ]

        messages = build_final_messages(
            state={
                "message": "Compare organizations.",
                "selection": selection,
                "tool_messages": tool_messages,
            },
            prompts=civic_prompt_snapshot,
        )

        assert messages[0] == SystemMessage(content=civic_prompt_snapshot.answer)
        assert messages[1] == HumanMessage(content="Compare organizations.")
        assert messages[2] == selection
        assert messages[3:] == tool_messages
        assert all("private" not in str(message.content) for message in messages)

    def test_requires_selection(self, civic_prompt_snapshot):
        with pytest.raises(CivicAssistantGraphError, match="missing the selection"):
            build_final_messages(state={"message": "Hello"}, prompts=civic_prompt_snapshot)

    def test_requires_tool_messages_when_tools_were_selected(self, civic_prompt_snapshot, organization_tool_call):
        selection = AIMessage(content="", tool_calls=[organization_tool_call("doh", "call-doh")])

        with pytest.raises(CivicAssistantGraphError, match="missing required tool evidence"):
            build_final_messages(
                state={"message": "Overview", "selection": selection},
                prompts=civic_prompt_snapshot,
            )


class TestPublicText:
    def test_returns_plain_ai_message_chunk_text(self):
        assert public_text(AIMessageChunk(content="public answer")) == "public answer"

    def test_does_not_return_reasoning_or_non_text_blocks(self):
        assert public_text(AIMessageChunk(content=[{"type": "reasoning", "reasoning": "private"}])) == ""
        assert public_text(AIMessageChunk(content=[{"type": "image_url", "image_url": {"url": "secret"}}])) == ""

    def test_returns_empty_for_non_ai_message_chunks(self):
        assert public_text(ToolMessage(content="tool evidence", tool_call_id="call-doh")) == ""
