from typing import Literal, NotRequired, TypedDict

from apps.organizations.models import Organization
from apps.users.models import User

ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH = 2_000


class OrganizationOverviewCallerUnavailableError(Exception):
    """Raised when the caller cannot access organization overview data."""


class OrganizationOverviewData(TypedDict):
    slug: str
    name: str
    description: str
    organization_type: str


class OrganizationOverviewLookupData(TypedDict):
    status: Literal["ok", "ambiguous", "not_found"]
    slug: NotRequired[str]
    name: NotRequired[str]
    description: NotRequired[str]
    organization_type: NotRequired[str]
    description_truncated: NotRequired[bool]


def read_organization_overview(
    *,
    caller_user_id: int | None,
    identifier: str,
) -> OrganizationOverviewLookupData:

    if caller_user_id is None:
        raise OrganizationOverviewCallerUnavailableError

    if not User.objects.filter(
        pk=caller_user_id,
        is_active=True,
    ).exists():
        raise OrganizationOverviewCallerUnavailableError

    organization = (
        Organization.objects.filter(slug__iexact=identifier)
        .values(
            "slug",
            "name",
            "description",
            "organization_type",
        )
        .first()
    )

    if organization is not None:
        return _organization_overview_data(organization)

    exact_name_matches = list(
        Organization.objects.filter(name__iexact=identifier)
        .order_by("name", "slug")
        .values(
            "slug",
            "name",
            "description",
            "organization_type",
        )[:2]
    )

    if len(exact_name_matches) == 1:
        return _organization_overview_data(exact_name_matches[0])

    if len(exact_name_matches) > 1:
        return {"status": "ambiguous"}

    partial_name_matches = list(
        Organization.objects.filter(name__icontains=identifier)
        .order_by("name", "slug")
        .values(
            "slug",
            "name",
            "description",
            "organization_type",
        )[:2]
    )

    if len(partial_name_matches) == 1:
        return _organization_overview_data(partial_name_matches[0])

    if len(partial_name_matches) > 1:
        return {"status": "ambiguous"}

    return {"status": "not_found"}


def _organization_overview_data(organization: OrganizationOverviewData) -> OrganizationOverviewLookupData:
    description = organization["description"]
    is_truncated = len(description) > ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH

    return {
        "status": "ok",
        "slug": organization["slug"],
        "name": organization["name"],
        "description": description[:ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH],
        "organization_type": organization["organization_type"],
        "description_truncated": is_truncated,
    }
