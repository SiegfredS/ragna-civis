import asyncio
from collections.abc import AsyncIterator
from unittest.mock import Mock

from apps.civic_assistant import runtime as runtime_module
from apps.civic_assistant.prompts import CivicPromptSnapshot
from apps.civic_assistant.runtime import CivicAssistantRuntime, prepare_civic_assistant_runtime


class TestPrepareCivicAssistantRuntime:
    def test_resolves_each_dependency_once_and_preserves_prepared_values(self, monkeypatch):
        prompts = CivicPromptSnapshot(selection="selection", answer="answer")
        model = Mock()
        load_prompts = Mock(return_value=prompts)
        build_model = Mock(return_value=model)
        monkeypatch.setattr(runtime_module, "load_civic_prompt_snapshot", load_prompts)
        monkeypatch.setattr(runtime_module, "build_civic_assistant_chat_model", build_model)

        runtime = prepare_civic_assistant_runtime(caller_user_id=123)

        load_prompts.assert_called_once_with()
        build_model.assert_called_once_with()
        assert runtime == CivicAssistantRuntime(caller_user_id=123, model=model, prompts=prompts)
        assert runtime.model is model
        assert runtime.prompts is prompts


class TrackingClient:
    def __init__(self, lifecycle: list[str]):
        self.lifecycle = lifecycle

    async def __aenter__(self):
        self.lifecycle.append("entered")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.lifecycle.append("exited")
        return False


class TrackingGraph:
    def __init__(self, lifecycle: list[str], events: list[dict[str, str]]):
        self.lifecycle = lifecycle
        self.events = events

    async def astream(self, input_data, *, stream_mode: str) -> AsyncIterator[dict[str, str]]:
        assert self.lifecycle == ["entered", "graph-built"]
        assert input_data == {"message": "Hello"}
        assert stream_mode == "custom"
        self.lifecycle.append("streamed")
        for event in self.events:
            yield event


class TestCivicAssistantRuntime:
    def test_stream_owns_request_local_client_lifecycle_and_yields_graph_events(self, monkeypatch):
        lifecycle: list[str] = []
        events = [
            {"type": "delta", "text": "Hello"},
            {"type": "delta", "text": " world"},
        ]
        client = TrackingClient(lifecycle)
        graph = TrackingGraph(lifecycle, events)
        create_client = Mock(return_value=client)

        def build_graph(*, model, mcp_client, prompts):
            assert lifecycle == ["entered"]
            assert mcp_client is client
            assert model is prepared_model
            assert prompts is prepared_prompts
            lifecycle.append("graph-built")
            return graph

        build_graph_mock = Mock(side_effect=build_graph)
        monkeypatch.setattr(runtime_module, "create_civic_assistant_mcp_client", create_client)
        monkeypatch.setattr(runtime_module, "build_civic_assistant_graph", build_graph_mock)
        prepared_model = Mock()
        prepared_prompts = CivicPromptSnapshot(selection="selection", answer="answer")
        runtime = CivicAssistantRuntime(caller_user_id=123, model=prepared_model, prompts=prepared_prompts)

        streamed_events = asyncio.run(_collect_events(runtime))

        create_client.assert_called_once_with(caller_user_id=123)
        build_graph_mock.assert_called_once_with(
            model=prepared_model,
            mcp_client=client,
            prompts=prepared_prompts,
        )
        assert streamed_events == events
        assert all(streamed is expected for streamed, expected in zip(streamed_events, events, strict=True))
        assert lifecycle == ["entered", "graph-built", "streamed", "exited"]


async def _collect_events(runtime: CivicAssistantRuntime) -> list[dict[str, str]]:
    return [event async for event in runtime.stream(message="Hello")]
