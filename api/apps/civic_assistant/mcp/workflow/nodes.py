import asyncio
from typing import Any, Literal, cast

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langgraph.config import get_stream_writer
from pydantic import ValidationError

from apps.civic_assistant.mcp.tools.organizations import ORGANIZATION_OVERVIEW_TOOL_NAME
from apps.civic_assistant.mcp.workflow.constants import ANSWER_NODE, LOOKUP_NODE
from apps.civic_assistant.mcp.workflow.errors import CivicAssistantGraphError
from apps.civic_assistant.mcp.workflow.schemas import OrganizationOverviewToolArguments
from apps.civic_assistant.mcp.workflow.state import CivicAssistantState, CivicAssistantStateUpdate
from apps.civic_assistant.prompts import CivicPromptSnapshot

MODEL_CALL_TIMEOUT_SECONDS = 30
MAX_TOOL_CALLS_PER_REQUEST = 5

SelectionRoute = Literal["lookup", "answer"]


async def select_tool(
    state: CivicAssistantState, *, selecting_model: Runnable[Any, BaseMessage], prompts: CivicPromptSnapshot
) -> CivicAssistantStateUpdate:
    """Privately decide which supported lookups are needed."""

    async with asyncio.timeout(MODEL_CALL_TIMEOUT_SECONDS):
        response = await selecting_model.ainvoke(
            [
                SystemMessage(content=prompts.selection),
                HumanMessage(content=state["message"]),
            ]
        )

    if not isinstance(response, AIMessage):
        raise CivicAssistantGraphError("The selection model returned an invalid response.")

    return {"selection": _sanitize_selection(response)}


def choose_after_selection(
    state: CivicAssistantState,
) -> SelectionRoute:
    """Route to organization lookups or directly to final generation."""
    selection = state.get("selection")

    if selection is None:
        raise CivicAssistantGraphError("The selection node did not produce a result.")

    if selection.tool_calls:
        return cast(SelectionRoute, LOOKUP_NODE)

    return cast(SelectionRoute, ANSWER_NODE)


async def lookup(state: CivicAssistantState, *, overview_tool: BaseTool) -> CivicAssistantStateUpdate:
    """Execute the validated organization lookups."""

    selection = state.get("selection")

    if selection is None or not selection.tool_calls:
        raise CivicAssistantGraphError("The lookup node requires validated tool calls.")

    tool_messages: list[ToolMessage] = []

    for tool_call in selection.tool_calls:
        evidence = await overview_tool.ainvoke(tool_call["args"])

        if not isinstance(evidence, str):
            raise CivicAssistantGraphError("The organization overview tool returned invalid evidence.")

        tool_messages.append(
            ToolMessage(
                content=evidence,
                name=ORGANIZATION_OVERVIEW_TOOL_NAME,
                tool_call_id=tool_call["id"],
            )
        )

    return {"tool_messages": tool_messages}


async def answer(state: CivicAssistantState, *, model: BaseChatModel, prompts: CivicPromptSnapshot):
    """Generate and publicly stream only the final answer text."""
    messages = build_final_messages(
        state=state,
        prompts=prompts,
    )
    writer = get_stream_writer()

    async with asyncio.timeout(MODEL_CALL_TIMEOUT_SECONDS):
        async for chunk in model.astream(messages):
            text = public_text(chunk)

            if text:
                writer(
                    {
                        "type": "delta",
                        "text": text,
                    }
                )

    return {}


def public_text(
    chunk: BaseMessage,
) -> str:
    """Return only public final-answer text."""
    if not isinstance(chunk, AIMessageChunk):
        return ""

    return str(chunk.text)


def build_final_messages(*, state: CivicAssistantState, prompts: CivicPromptSnapshot) -> list[BaseMessage]:
    """Build final tool-free model context from trusted workflow state."""

    messages: list[BaseMessage] = [
        SystemMessage(content=prompts.answer),
        HumanMessage(content=state["message"]),
    ]

    selection = state.get("selection")

    if selection is None:
        raise CivicAssistantGraphError("Final generation is missing the selection result.")

    if not selection.tool_calls:
        return messages

    tool_messages = state.get("tool_messages")

    if tool_messages is None:
        raise CivicAssistantGraphError("Final generation is missing required tool evidence.")

    messages.append(selection)
    messages.extend(tool_messages)

    return messages


def _sanitize_selection(selection: AIMessage) -> AIMessage:
    """Validate model-selected tool calls and discard private prose."""
    if selection.invalid_tool_calls:
        raise CivicAssistantGraphError("The selection model returned an invalid tool call.")

    if len(selection.tool_calls) > MAX_TOOL_CALLS_PER_REQUEST:
        raise CivicAssistantGraphError("The selection model exceeded the tool-call budget.")

    if not selection.tool_calls:
        return AIMessage(content="")

    sanitized_tool_calls = []
    tool_call_ids: set[str] = set()

    for tool_call in selection.tool_calls:
        if tool_call["name"] != ORGANIZATION_OVERVIEW_TOOL_NAME:
            raise CivicAssistantGraphError("The selection model requested an unsupported tool.")

        tool_call_id = tool_call.get("id")

        if not isinstance(tool_call_id, str) or not tool_call_id.strip():
            raise CivicAssistantGraphError("The selection model returned a tool call without an ID.")

        if tool_call_id in tool_call_ids:
            raise CivicAssistantGraphError("The selection model returned duplicate tool-call IDs.")

        tool_call_ids.add(tool_call_id)

        try:
            arguments = OrganizationOverviewToolArguments.model_validate(tool_call["args"])
        except (KeyError, TypeError, ValidationError) as error:
            raise CivicAssistantGraphError("The selection model returned invalid tool arguments.") from error

        sanitized_tool_calls.append(
            {
                "name": ORGANIZATION_OVERVIEW_TOOL_NAME,
                "args": arguments.model_dump(),
                "id": tool_call_id,
                "type": "tool_call",
            }
        )

    # Only validated tool-call structures survive the private selection pass.
    return AIMessage(
        content="",
        tool_calls=sanitized_tool_calls,
    )
