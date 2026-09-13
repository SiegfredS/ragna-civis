import asyncio

import pytest
from mcp import Client, MCPError
from mcp.types import INTERNAL_ERROR

from apps.civic_assistant.mcp.client import create_civic_assistant_mcp_client
from apps.organizations.tests.factories import OrganizationFactory
from apps.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def allow_sync_database_access_from_mcp_task(monkeypatch):
    # The shared MCP fixture executes sync tools directly because worker threads
    # are unavailable in this test environment.
    monkeypatch.setenv("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


async def open_and_close_client(client: Client) -> None:
    async with client:
        pass


async def list_client_tools(client: Client):
    async with client:
        return await client.list_tools()


async def call_client_tool(client: Client, identifier: str):
    async with client:
        return await client.call_tool("get_organization_overview", {"identifier": identifier})


async def call_client_tool_expect_mcp_error(client: Client, identifier: str) -> MCPError:
    async with client:
        with pytest.raises(MCPError) as error_info:
            await client.call_tool("get_organization_overview", {"identifier": identifier})
        return error_info.value


@pytest.mark.django_db(transaction=True)
class TestCivicAssistantMCPClient:
    def test_returns_an_official_mcp_client(self, user):
        client = create_civic_assistant_mcp_client(caller_user_id=user.pk)

        assert isinstance(client, Client)

    def test_opens_and_closes_an_in_process_connection(self, user):
        client = create_civic_assistant_mcp_client(caller_user_id=user.pk)

        asyncio.run(open_and_close_client(client))

    def test_exposes_the_registered_organization_tool(self, user):
        client = create_civic_assistant_mcp_client(caller_user_id=user.pk)

        tools = asyncio.run(list_client_tools(client))

        assert [tool.name for tool in tools.tools] == ["get_organization_overview"]

    def test_calls_the_organization_tool_end_to_end(self, user):
        organization = OrganizationFactory(
            name="Civic Test Organization",
            description="A bounded organization overview.",
        )
        client = create_civic_assistant_mcp_client(caller_user_id=user.pk)

        result = asyncio.run(call_client_tool(client, organization.slug))

        assert result.is_error is False
        assert result.structured_content["slug"] == organization.slug

    def test_resolves_a_unique_partial_name(self, user):
        organization = OrganizationFactory(name="Liyue Qixing", slug="liyue-qixing")
        client = create_civic_assistant_mcp_client(caller_user_id=user.pk)

        result = asyncio.run(call_client_tool(client, "liyue"))

        assert result.is_error is False
        assert result.structured_content["slug"] == organization.slug

    def test_returns_ambiguous_for_multiple_partial_name_matches(self, user):
        OrganizationFactory(name="Liyue Qixing", slug="liyue-qixing")
        OrganizationFactory(name="Liyue Harbor", slug="liyue-harbor")
        client = create_civic_assistant_mcp_client(caller_user_id=user.pk)

        result = asyncio.run(call_client_tool(client, "liyue"))

        assert result.is_error is False
        assert result.structured_content == {"status": "ambiguous"}

    def test_separate_clients_retain_their_callers(self):
        active_user = UserFactory()
        inactive_user = UserFactory(is_active=False)
        organization = OrganizationFactory()
        active_client = create_civic_assistant_mcp_client(caller_user_id=active_user.pk)
        inactive_client = create_civic_assistant_mcp_client(caller_user_id=inactive_user.pk)

        active_result = asyncio.run(call_client_tool(active_client, organization.slug))

        assert active_result.structured_content["slug"] == organization.slug
        error = asyncio.run(call_client_tool_expect_mcp_error(inactive_client, organization.slug))

        assert error.error.code == INTERNAL_ERROR

    def test_invalid_caller_failure_reaches_the_client(self):
        organization = OrganizationFactory()
        client = create_civic_assistant_mcp_client(caller_user_id=0)

        error = asyncio.run(call_client_tool_expect_mcp_error(client, organization.slug))

        assert error.error.code == INTERNAL_ERROR

    def test_missing_organization_returns_a_controlled_result(self, user):
        client = create_civic_assistant_mcp_client(caller_user_id=user.pk)

        result = asyncio.run(call_client_tool(client, "missing-organization"))

        assert result.is_error is False
        assert result.structured_content == {"status": "not_found"}
