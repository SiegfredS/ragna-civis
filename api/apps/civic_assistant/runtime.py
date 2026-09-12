import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel

from apps.civic_assistant.chat_model import build_civic_assistant_chat_model
from apps.civic_assistant.mcp.client import create_civic_assistant_mcp_client
from apps.civic_assistant.mcp.workflow.graph import build_civic_assistant_graph
from apps.civic_assistant.prompts import CivicPromptSnapshot, load_civic_prompt_snapshot

RUNTIME_TIMEOUT_SECONDS = 75

CivicAssistantStreamEvent = dict[str, str]


@dataclass(frozen=True, slots=True)
class CivicAssistantRuntime:
    """Prepared dependencies for one Civic Assistant request."""

    caller_user_id: int
    model: BaseChatModel
    prompts: CivicPromptSnapshot

    async def stream(self, *, message: str) -> AsyncGenerator[CivicAssistantStreamEvent, None]:
        """Run one request-local Civic Assistant execution."""
        client = create_civic_assistant_mcp_client(
            caller_user_id=self.caller_user_id,
        )

        async with asyncio.timeout(RUNTIME_TIMEOUT_SECONDS):
            async with client:
                graph = build_civic_assistant_graph(
                    model=self.model,
                    mcp_client=client,
                    prompts=self.prompts,
                )

                async for event in graph.astream({"message": message}, stream_mode="custom"):
                    yield event


def prepare_civic_assistant_runtime(*, caller_user_id: int) -> CivicAssistantRuntime:
    """Resolve trusted dependencies before streaming starts."""
    prompts = load_civic_prompt_snapshot()
    model = build_civic_assistant_chat_model()

    return CivicAssistantRuntime(
        caller_user_id=caller_user_id,
        prompts=prompts,
        model=model,
    )
