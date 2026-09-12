import asyncio
from typing import Any
from unittest.mock import Mock

import pytest
from mcp import MCPError
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import INTERNAL_ERROR

from apps.civic_assistant.mcp.server import create_civic_assistant_mcp_server
from apps.civic_assistant.mcp.tools import organizations as organization_tools_module
from apps.organizations.queries.overview import (
    ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH,
    OrganizationOverviewCallerUnavailableError,
    OrganizationOverviewNotFoundError,
)
from apps.users.tests.factories import UserFactory


def call_tool(server: MCPServer, arguments: dict[str, Any]) -> Any:
    return asyncio.run(server.call_tool("get_organization_overview", arguments))


@pytest.mark.django_db
class TestOrganizationOverviewTool:
    def test_exposes_only_slug_and_the_requested_schemas(self):
        server = create_civic_assistant_mcp_server(caller_user_id=1)
        tool = asyncio.run(server.list_tools())[0]

        assert tool.input_schema["required"] == ["slug"]
        assert set(tool.input_schema["properties"]) == {"slug"}
        assert tool.input_schema["properties"]["slug"] == {
            "maxLength": 255,
            "minLength": 1,
            "pattern": r"^[A-Za-z0-9_-]+$",
            "title": "Slug",
            "type": "string",
        }
        assert tool.output_schema is not None
        assert set(tool.output_schema["properties"]) == {
            "slug",
            "name",
            "description",
            "organization_type",
            "description_truncated",
        }
        assert tool.output_schema["required"] == [
            "slug",
            "name",
            "description",
            "organization_type",
            "description_truncated",
        ]

    def test_invokes_the_registered_tool_with_structured_output(self, user, monkeypatch):
        overview = {
            "slug": "civic-test-organization",
            "name": "Civic Test Organization",
            "description": "A bounded organization overview.",
            "organization_type": "civic_organization",
            "description_truncated": False,
        }
        read_overview = Mock(return_value=overview)
        monkeypatch.setattr(organization_tools_module, "read_organization_overview", read_overview)
        server = create_civic_assistant_mcp_server(caller_user_id=user.pk)

        result = call_tool(server, {"slug": overview["slug"]})

        assert result.structured_content == overview
        assert result.is_error is False
        read_overview.assert_called_once_with(caller_user_id=user.pk, slug=overview["slug"])

    def test_fresh_servers_retain_different_callers(self, monkeypatch):
        active_user = UserFactory()
        inactive_user = UserFactory(is_active=False)
        overview = {
            "slug": "civic-test-organization",
            "name": "Civic Test Organization",
            "description": "A bounded organization overview.",
            "organization_type": "civic_organization",
            "description_truncated": False,
        }

        def read_overview(*, caller_user_id, slug):
            if caller_user_id == active_user.pk:
                return overview
            raise OrganizationOverviewCallerUnavailableError

        monkeypatch.setattr(organization_tools_module, "read_organization_overview", read_overview)
        active_server = create_civic_assistant_mcp_server(caller_user_id=active_user.pk)
        inactive_server = create_civic_assistant_mcp_server(caller_user_id=inactive_user.pk)

        active_result = call_tool(active_server, {"slug": overview["slug"]})

        assert active_result.structured_content["slug"] == overview["slug"]
        with pytest.raises(MCPError) as error_info:
            call_tool(inactive_server, {"slug": overview["slug"]})
        assert error_info.value.error.code == INTERNAL_ERROR

    def test_missing_organization_is_a_recoverable_tool_error(self, user, monkeypatch):
        monkeypatch.setattr(
            organization_tools_module,
            "read_organization_overview",
            Mock(side_effect=OrganizationOverviewNotFoundError),
        )
        server = create_civic_assistant_mcp_server(caller_user_id=user.pk)

        with pytest.raises(ToolError) as error_info:
            call_tool(server, {"slug": "missing-organization"})

        assert "No organization exists with slug 'missing-organization'." in str(error_info.value)
        assert isinstance(error_info.value.__cause__, ToolError)
        assert isinstance(error_info.value.__cause__.__cause__, OrganizationOverviewNotFoundError)

    def test_unavailable_caller_is_a_protocol_error(self, monkeypatch):
        inactive_user = UserFactory(is_active=False)
        monkeypatch.setattr(
            organization_tools_module,
            "read_organization_overview",
            Mock(side_effect=OrganizationOverviewCallerUnavailableError),
        )
        server = create_civic_assistant_mcp_server(caller_user_id=inactive_user.pk)

        with pytest.raises(MCPError) as error_info:
            call_tool(server, {"slug": "civic-test-organization"})

        assert error_info.value.error.code == INTERNAL_ERROR
        assert error_info.value.error.message == "The caller cannot access organization overview data."
        assert isinstance(error_info.value.__cause__, OrganizationOverviewCallerUnavailableError)

    @pytest.mark.parametrize(
        "slug",
        ["", "a" * 256, "has spaces", "has/slash"],
    )
    def test_rejects_invalid_slug_before_domain_access(self, user, slug, monkeypatch):
        read_overview = Mock(wraps=organization_tools_module.read_organization_overview)
        monkeypatch.setattr(organization_tools_module, "read_organization_overview", read_overview)
        server = create_civic_assistant_mcp_server(caller_user_id=user.pk)

        with pytest.raises(ToolError):
            call_tool(server, {"slug": slug})

        read_overview.assert_not_called()

    def test_preserves_domain_description_truncation(self, user, monkeypatch):
        description = "a" * (ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH + 1)
        overview = {
            "slug": "long-description-organization",
            "name": "Long Description Organization",
            "description": description[:ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH],
            "organization_type": "civic_organization",
            "description_truncated": True,
        }
        monkeypatch.setattr(organization_tools_module, "read_organization_overview", Mock(return_value=overview))
        server = create_civic_assistant_mcp_server(caller_user_id=user.pk)

        result = call_tool(server, {"slug": overview["slug"]})

        assert len(result.structured_content["description"]) == ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH
        assert result.structured_content["description_truncated"] is True
