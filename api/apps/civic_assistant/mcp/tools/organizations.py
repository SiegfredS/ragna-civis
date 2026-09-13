from typing import Annotated

from mcp import MCPError
from mcp.server import MCPServer
from mcp.types import INTERNAL_ERROR, ToolAnnotations
from pydantic import Field, StringConstraints

from apps.organizations.queries.overview import (
    OrganizationOverviewCallerUnavailableError,
    OrganizationOverviewLookupData,
    read_organization_overview,
)

ORGANIZATION_OVERVIEW_TOOL_NAME = "get_organization_overview"
ORGANIZATION_OVERVIEW_TOOL_DESCRIPTION = (
    "Return the Ragna Civis overview for a uniquely resolved organization name, partial name, or slug. "
    "Do not guess identifiers; use the organization term from the user's request."
)

OrganizationIdentifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]

OrganizationSlug = Annotated[
    str,
    Field(
        min_length=1,
        max_length=255,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
]


class OrganizationTools:
    def __init__(self, *, caller_user_id: int) -> None:
        self.caller_user_id = caller_user_id

    def get_organization_overview(self, identifier: OrganizationIdentifier) -> OrganizationOverviewLookupData:
        try:
            return read_organization_overview(
                caller_user_id=self.caller_user_id,
                identifier=identifier,
            )
        except OrganizationOverviewCallerUnavailableError as error:
            raise MCPError(
                code=INTERNAL_ERROR,
                message="The caller cannot access organization overview data.",
            ) from error


def register_organization_tools(*, mcp_server: MCPServer, caller_user_id: int) -> None:
    organization_tools = OrganizationTools(
        caller_user_id=caller_user_id,
    )

    mcp_server.add_tool(
        organization_tools.get_organization_overview,
        name=ORGANIZATION_OVERVIEW_TOOL_NAME,
        description=ORGANIZATION_OVERVIEW_TOOL_DESCRIPTION,
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        ),
        structured_output=True,
    )
