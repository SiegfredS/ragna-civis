import asyncio
import json
from types import SimpleNamespace

import pytest
from mcp import MCPError

from apps.civic_assistant.mcp.workflow import tools as workflow_tools
from apps.civic_assistant.mcp.workflow.errors import CivicAssistantMCPToolError
from apps.civic_assistant.mcp.workflow.tools import create_organization_overview_tool


def mcp_result(*, structured_content=None, is_error=False, content=None):
    return SimpleNamespace(structured_content=structured_content, is_error=is_error, content=content)


class TestCreateOrganizationOverviewTool:
    def test_returns_validated_json_for_a_structured_mcp_response(self, mcp_client, organization_payload):
        payload = organization_payload("doh")
        mcp_client.call_tool.return_value = mcp_result(structured_content=payload)
        tool = create_organization_overview_tool(client=mcp_client)

        result = asyncio.run(tool.ainvoke({"slug": "doh"}))

        assert json.loads(result) == {"status": "ok", "organization": payload}
        mcp_client.call_tool.assert_awaited_once_with("get_organization_overview", {"slug": "doh"})

    def test_supports_multiple_sequential_calls(self, mcp_client, organization_payload):
        mcp_client.call_tool.side_effect = [
            mcp_result(structured_content=organization_payload("doh")),
            mcp_result(structured_content=organization_payload("deped")),
        ]
        tool = create_organization_overview_tool(client=mcp_client)

        results = asyncio.run(
            _invoke_tool_twice(
                tool,
                "doh",
                "deped",
            )
        )

        assert [json.loads(result)["organization"]["slug"] for result in results] == ["doh", "deped"]
        assert mcp_client.call_tool.await_args_list[0].args == ("get_organization_overview", {"slug": "doh"})
        assert mcp_client.call_tool.await_args_list[1].args == ("get_organization_overview", {"slug": "deped"})

    def test_returns_only_unavailable_for_an_error_result(self, mcp_client):
        mcp_client.call_tool.return_value = mcp_result(is_error=True)
        tool = create_organization_overview_tool(client=mcp_client)

        result = asyncio.run(tool.ainvoke({"slug": "doh"}))

        assert result == '{"status":"unavailable"}'

    def test_does_not_leak_mcp_error_text(self, mcp_client):
        mcp_client.call_tool.return_value = mcp_result(
            is_error=True,
            content=[{"type": "text", "text": "secret internal error"}],
        )
        tool = create_organization_overview_tool(client=mcp_client)

        result = asyncio.run(tool.ainvoke({"slug": "doh"}))

        assert "internal" not in result
        assert "secret" not in result

    def test_raises_for_malformed_structured_content(self, mcp_client, organization_payload):
        payload = organization_payload("doh")
        payload["unexpected"] = "not allowed"
        mcp_client.call_tool.return_value = mcp_result(structured_content=payload)
        tool = create_organization_overview_tool(client=mcp_client)

        with pytest.raises(CivicAssistantMCPToolError, match="result was invalid"):
            asyncio.run(tool.ainvoke({"slug": "doh"}))

    def test_raises_for_an_mcp_protocol_failure(self, mcp_client):
        mcp_client.call_tool.side_effect = MCPError(code=-32603, message="secret protocol details")
        tool = create_organization_overview_tool(client=mcp_client)

        with pytest.raises(CivicAssistantMCPToolError, match="lookup failed") as error_info:
            asyncio.run(tool.ainvoke({"slug": "doh"}))

        assert "secret protocol details" not in str(error_info.value)

    def test_raises_for_a_timeout_without_waiting(self, mcp_client, monkeypatch):
        class ImmediateTimeout:
            async def __aenter__(self):
                raise TimeoutError

            async def __aexit__(self, exc_type, exc_value, traceback):
                return False

        monkeypatch.setattr(workflow_tools.asyncio, "timeout", lambda _: ImmediateTimeout())
        tool = create_organization_overview_tool(client=mcp_client)

        with pytest.raises(CivicAssistantMCPToolError, match="lookup timed out"):
            asyncio.run(tool.ainvoke({"slug": "doh"}))


async def _invoke_tool_twice(tool, first_slug: str, second_slug: str) -> tuple[str, str]:
    return await tool.ainvoke({"slug": first_slug}), await tool.ainvoke({"slug": second_slug})
