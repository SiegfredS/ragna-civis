from pydantic import BaseModel, ConfigDict, Field

from apps.civic_assistant.mcp.tools.organizations import OrganizationSlug
from apps.organizations.queries.overview import ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH


class OrganizationOverviewToolArguments(BaseModel):
    """Arguments exposed to the selection model."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    slug: OrganizationSlug


class OrganizationOverviewEvidence(BaseModel):
    """Validated allowlist projected from the MCP structured result."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    slug: OrganizationSlug
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    description: str = Field(max_length=ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH)
    organization_type: str
    description_truncated: bool
