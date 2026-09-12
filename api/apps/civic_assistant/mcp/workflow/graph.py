from functools import partial

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from mcp import Client

from apps.civic_assistant.mcp.workflow.constants import ANSWER_NODE, LOOKUP_NODE, SELECTION_NODE
from apps.civic_assistant.mcp.workflow.nodes import answer, choose_after_selection, lookup, select_tool
from apps.civic_assistant.mcp.workflow.state import CivicAssistantState
from apps.civic_assistant.mcp.workflow.tools import create_organization_overview_tool
from apps.civic_assistant.prompts import CivicPromptSnapshot


def build_civic_assistant_graph(*, model: BaseChatModel, mcp_client: Client, prompts: CivicPromptSnapshot):
    """Build one bounded Civic Assistant execution graph."""

    overview_tool = create_organization_overview_tool(
        client=mcp_client,
    )

    selecting_model = model.bind_tools(
        [overview_tool],
        strict=True,
        parallel_tool_calls=True,
    )
    graph = StateGraph(CivicAssistantState)

    graph.add_node(
        SELECTION_NODE,
        partial(
            select_tool,
            selecting_model=selecting_model,
            prompts=prompts,
        ),
    )

    graph.add_node(
        LOOKUP_NODE,
        partial(
            lookup,
            overview_tool=overview_tool,
        ),
    )

    graph.add_node(
        ANSWER_NODE,
        partial(
            answer,
            model=model,
            prompts=prompts,
        ),
    )

    graph.add_edge(
        START,
        SELECTION_NODE,
    )

    graph.add_conditional_edges(
        SELECTION_NODE,
        choose_after_selection,
        {
            LOOKUP_NODE: LOOKUP_NODE,
            ANSWER_NODE: ANSWER_NODE,
        },
    )

    graph.add_edge(LOOKUP_NODE, ANSWER_NODE)

    graph.add_edge(ANSWER_NODE, END)

    return graph.compile()
