import asyncio
import json
import logging

from langchain_core.tools import StructuredTool
from mcp import Client, MCPError
from pydantic import ValidationError

from apps.civic_assistant.mcp.tools.organizations import (
    ORGANIZATION_OVERVIEW_TOOL_DESCRIPTION,
    ORGANIZATION_OVERVIEW_TOOL_NAME,
)
from apps.civic_assistant.mcp.workflow.errors import CivicAssistantMCPToolError
from apps.civic_assistant.mcp.workflow.schemas import OrganizationOverviewEvidence, OrganizationOverviewToolArguments

MCP_TOOL_TIMEOUT_SECONDS = 10

logger = logging.getLogger(__name__)


def create_organization_overview_tool(*, client: Client) -> StructuredTool:
    """Adapt the request-local MCP capability for LangChain."""

    async def get_organization_overview(
        slug: str,
    ) -> str:
        arguments = OrganizationOverviewToolArguments.model_validate({"slug": slug})

        try:
            async with asyncio.timeout(MCP_TOOL_TIMEOUT_SECONDS):
                result = await client.call_tool(
                    ORGANIZATION_OVERVIEW_TOOL_NAME,
                    arguments.model_dump(),
                )
                logger.debug(
                    "Calling Civic Assistant MCP tool %s for slug=%s",
                    ORGANIZATION_OVERVIEW_TOOL_NAME,
                    slug,
                )
        except TimeoutError as error:
            raise CivicAssistantMCPToolError("The organization overview lookup timed out.") from error
        except MCPError as error:
            raise CivicAssistantMCPToolError("The organization overview lookup failed.") from error

        if result.is_error:
            return json.dumps(
                {"status": "unavailable"},
                separators=(",", ":"),
            )

        try:
            overview = OrganizationOverviewEvidence.model_validate(result.structured_content)

        except ValidationError as error:
            raise CivicAssistantMCPToolError("The organization overview result was invalid.") from error

        return json.dumps({"status": "ok", "organization": overview.model_dump()}, separators=(",", ":"))

    # coroutine because we use async function
    structured_tool = StructuredTool.from_function(
        coroutine=get_organization_overview,
        name=ORGANIZATION_OVERVIEW_TOOL_NAME,
        description=ORGANIZATION_OVERVIEW_TOOL_DESCRIPTION,
        args_schema=OrganizationOverviewToolArguments,
    )
    return structured_tool
