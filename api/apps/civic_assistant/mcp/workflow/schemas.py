from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from apps.civic_assistant.mcp.tools.organizations import OrganizationIdentifier, OrganizationSlug
from apps.organizations.queries.overview import ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH


class OrganizationOverviewToolArguments(BaseModel):
    """Arguments exposed to the selection model."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    identifier: OrganizationIdentifier


class OrganizationOverviewEvidence(BaseModel):
    """Validated allowlist projected from the MCP structured result."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    status: Literal["ok"]
    slug: OrganizationSlug
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    description: str = Field(max_length=ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH)
    organization_type: str
    description_truncated: bool


class OrganizationOverviewAmbiguousEvidence(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    status: Literal["ambiguous"]


class OrganizationOverviewNotFoundEvidence(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    status: Literal["not_found"]


organization_overview_result_adapter = TypeAdapter(
    OrganizationOverviewEvidence | OrganizationOverviewAmbiguousEvidence | OrganizationOverviewNotFoundEvidence
)
