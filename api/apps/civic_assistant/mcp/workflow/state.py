from typing import NotRequired, TypedDict

from langchain_core.messages import AIMessage, ToolMessage


class CivicAssistantState(TypedDict):
    """State carried through one bounded Civic Assistant execution."""

    message: str
    selection: NotRequired[AIMessage]
    tool_messages: NotRequired[list[ToolMessage]]


class CivicAssistantStateUpdate(TypedDict, total=False):
    """Partial state update returned by a graph node."""

    selection: AIMessage
    tool_messages: list[ToolMessage]
