from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, Mock

import langgraph._internal._runnable as langgraph_runnable
import pytest
from langchain_core.messages import AIMessageChunk, BaseMessage
from mcp import Client

from apps.civic_assistant.prompts import CivicPromptSnapshot


@pytest.fixture
def civic_prompt_snapshot() -> CivicPromptSnapshot:
    return CivicPromptSnapshot(
        selection="Select only the organization lookups needed.",
        answer="Answer the user's question using the supplied evidence.",
    )


@pytest.fixture
def mcp_client() -> Mock:
    client = Mock(spec=Client)
    client.call_tool = AsyncMock()
    return client


@pytest.fixture(autouse=True)
def run_sync_graph_nodes_without_worker_threads(monkeypatch):
    async def run_in_executor(_executor, function, *args, **kwargs):
        return function(*args, **kwargs)

    # The locked test environment leaves LangGraph's executor thread alive after
    # a graph stream. Keep sync routing nodes deterministic and process-safe.
    monkeypatch.setattr(langgraph_runnable, "run_in_executor", run_in_executor)


def make_organization_payload(slug: str) -> dict[str, Any]:
    return {
        "status": "ok",
        "slug": slug,
        "name": f"{slug.upper()} Organization",
        "description": f"A bounded overview for {slug}.",
        "organization_type": "civic_organization",
        "description_truncated": False,
    }


def make_organization_tool_call(identifier: str, tool_call_id: str) -> dict[str, Any]:
    return {
        "name": "get_organization_overview",
        "args": {"identifier": identifier},
        "id": tool_call_id,
        "type": "tool_call",
    }


@pytest.fixture
def organization_payload():
    return make_organization_payload


@pytest.fixture
def organization_tool_call():
    return make_organization_tool_call


class FakeSelectionModel:
    def __init__(self, response: BaseMessage | str):
        self.response = response
        self.calls: list[list[BaseMessage]] = []

    async def ainvoke(self, messages: list[BaseMessage]) -> BaseMessage | str:
        self.calls.append(messages)
        return self.response


class FakeFinalModel:
    def __init__(self, selection_response: BaseMessage | str, chunks: list[AIMessageChunk]):
        self.selection_model = FakeSelectionModel(selection_response)
        self.chunks = chunks
        self.calls: list[list[BaseMessage]] = []
        self.bound_tools: list[Any] = []
        self.bind_kwargs: dict[str, Any] = {}

    def bind_tools(self, tools: list[Any], **kwargs: Any) -> FakeSelectionModel:
        self.bound_tools = tools
        self.bind_kwargs = kwargs
        return self.selection_model

    async def astream(self, messages: list[BaseMessage]) -> AsyncIterator[AIMessageChunk]:
        self.calls.append(messages)
        for chunk in self.chunks:
            yield chunk
