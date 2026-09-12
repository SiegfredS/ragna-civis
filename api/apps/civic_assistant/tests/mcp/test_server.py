import asyncio

import pytest

from apps.civic_assistant.mcp.server import create_civic_assistant_mcp_server


@pytest.mark.django_db
class TestCivicAssistantMCPServer:
    def test_exposes_only_the_organization_overview_tool(self):
        server = create_civic_assistant_mcp_server(caller_user_id=1)

        tools = asyncio.run(server.list_tools())

        assert [tool.name for tool in tools] == ["get_organization_overview"]
        tool = tools[0]
        assert tool.annotations is not None
        assert tool.annotations.read_only_hint is True
        assert tool.annotations.open_world_hint is False
