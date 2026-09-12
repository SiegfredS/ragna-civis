from mcp import Client

from apps.civic_assistant.mcp.server import create_civic_assistant_mcp_server


def create_civic_assistant_mcp_client(
    *,
    caller_user_id: int,
) -> Client:
    """Create an in-process MCP client for one Civic Assistant runtime."""
    mcp_server = create_civic_assistant_mcp_server(
        caller_user_id=caller_user_id,
    )

    return Client(mcp_server)
