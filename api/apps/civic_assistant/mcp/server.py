from mcp.server import MCPServer

from apps.civic_assistant.mcp.tools.organizations import register_organization_tools


def create_civic_assistant_mcp_server(*, caller_user_id: int) -> MCPServer:
    mcp_server = MCPServer("ragna-civis-civic-assistant")

    register_organization_tools(
        mcp_server=mcp_server,
        caller_user_id=caller_user_id,
    )

    return mcp_server
