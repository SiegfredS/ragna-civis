from typing import TypedDict

from apps.organizations.models import Organization
from apps.users.models import User

ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH = 2_000


class OrganizationOverviewCallerUnavailableError(Exception):
    """Raised when the caller cannot access organization overview data."""


class OrganizationOverviewNotFoundError(Exception):
    """Raised when the requested organization does not exist."""


class OrganizationOverviewData(TypedDict):
    slug: str
    name: str
    description: str
    organization_type: str
    description_truncated: bool


def read_organization_overview(
    *,
    caller_user_id: int | None,
    slug: str,
) -> OrganizationOverviewData:

    if caller_user_id is None:
        raise OrganizationOverviewCallerUnavailableError

    if not User.objects.filter(
        pk=caller_user_id,
        is_active=True,
    ).exists():
        raise OrganizationOverviewCallerUnavailableError

    organization = (
        Organization.objects.filter(slug=slug)
        .values(
            "slug",
            "name",
            "description",
            "organization_type",
        )
        .first()
    )

    if organization is None:
        raise OrganizationOverviewNotFoundError

    description = organization["description"]
    is_truncated = len(description) > ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH

    data: OrganizationOverviewData = {
        "slug": organization["slug"],
        "name": organization["name"],
        "description": description[:ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH],
        "organization_type": organization["organization_type"],
        "description_truncated": is_truncated,
    }

    return data
