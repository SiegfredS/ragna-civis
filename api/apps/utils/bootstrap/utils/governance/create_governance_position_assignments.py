from datetime import date
from typing import Any

from apps.governance.models import GovernancePositionAssignment
from apps.organizations.models import OrganizationMembership
from apps.utils.bootstrap.utils.lookups.governance import get_governance_body, get_governance_position
from apps.utils.bootstrap.utils.lookups.organization import get_organization
from apps.utils.bootstrap.utils.lookups.user_profiles import get_user_profile


def create_governance_position_assignments(
    data: list[dict[str, Any]],
) -> dict[tuple[str, str, str, str, date | None, date | None], GovernancePositionAssignment]:
    """Create assignments keyed by their scoped position, user, and date period."""
    assignments: dict[tuple[str, str, str, str, date | None, date | None], GovernancePositionAssignment] = {}

    for assignment_data in data:
        identity, assignment = create_governance_position_assignment(data=assignment_data)
        assignments[identity] = assignment

    return assignments


def create_governance_position_assignment(
    data: dict[str, Any],
) -> tuple[tuple[str, str, str, str, date | None, date | None], GovernancePositionAssignment]:
    organization_slug = data["organization"]
    governance_body_name = data["governance_body"]
    position_name = data["position"]
    username = data["user"]
    start_date = _parse_date(data.get("start_date"), field_name="start_date")
    end_date = _parse_date(data.get("end_date"), field_name="end_date")

    organization = get_organization(slug=organization_slug)
    governance_body = get_governance_body(organization_slug=organization_slug, name=governance_body_name)
    governance_position = get_governance_position(
        organization_slug=organization_slug,
        governance_body_name=governance_body_name,
        name=position_name,
    )
    user_profile = get_user_profile(username=username)

    memberships = OrganizationMembership.objects.filter(organization=organization, user_profile=user_profile)
    try:
        membership = memberships.get()
    except OrganizationMembership.DoesNotExist as error:
        raise ValueError(
            f"Bootstrap membership for user {username!r} in organization {organization_slug!r} does not exist."
        ) from error
    except OrganizationMembership.MultipleObjectsReturned as error:
        raise ValueError(
            f"Multiple memberships found for user {username!r} in organization {organization_slug!r}."
        ) from error

    if (
        governance_body.organization.pk != organization.pk
        or governance_position.governance_body.pk != governance_body.pk
    ):
        raise ValueError(
            f"Bootstrap governance position {position_name!r} does not belong to the referenced governance body "
            f"and organization."
        )

    assignments = GovernancePositionAssignment.objects.filter(
        membership=membership,
        position=governance_position,
        start_date=start_date,
        end_date=end_date,
    )
    try:
        assignment = assignments.get()
    except GovernancePositionAssignment.DoesNotExist:
        assignment = GovernancePositionAssignment(
            membership=membership,
            position=governance_position,
            start_date=start_date,
            end_date=end_date,
        )
    except GovernancePositionAssignment.MultipleObjectsReturned as error:
        raise ValueError(
            f"Multiple bootstrap assignments found for user {username!r}, position {position_name!r}, "
            f"and date period {start_date!r} to {end_date!r}."
        ) from error

    assignment.full_clean()
    assignment.save()

    return (
        organization_slug,
        governance_body_name,
        position_name,
        username,
        start_date,
        end_date,
    ), assignment


def _parse_date(value: Any, *, field_name: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError(f"Bootstrap {field_name} must be an ISO date string or null.")

    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Bootstrap {field_name} {value!r} is not a valid ISO date.") from error
