from typing import Any

from apps.governance.models import GovernancePosition
from apps.utils.bootstrap.utils.lookups.governance import get_governance_body
from apps.utils.bootstrap.utils.lookups.organization import get_organization


def create_governance_positions(data: list[dict[str, Any]]) -> dict[tuple[str, str, str], GovernancePosition]:
    """Create bootstrap governance positions keyed by organization, body, and name."""
    governance_positions: dict[tuple[str, str, str], GovernancePosition] = {}

    for governance_position_data in data:
        identity, governance_position = create_governance_position(data=governance_position_data)
        governance_positions[identity] = governance_position

    return governance_positions


def create_governance_position(data: dict[str, Any]) -> tuple[tuple[str, str, str], GovernancePosition]:
    organization_slug = data["organization"]
    governance_body_name = data["governance_body"]
    name = data["name"]
    organization = get_organization(slug=organization_slug)
    governance_body = get_governance_body(organization_slug=organization_slug, name=governance_body_name)

    if governance_body.organization.pk != organization.pk:
        raise ValueError(
            f"Bootstrap governance body {governance_body_name!r} does not belong to organization {organization_slug!r}."
        )

    try:
        governance_position = GovernancePosition.objects.get(governance_body=governance_body, name=name)
    except GovernancePosition.DoesNotExist:
        governance_position = GovernancePosition(governance_body=governance_body, name=name)
    except GovernancePosition.MultipleObjectsReturned as error:
        raise ValueError(
            f"Multiple governance positions named {name!r} found in body {governance_body_name!r} "
            f"for organization {organization_slug!r}."
        ) from error

    governance_position.description = data.get("description", "")
    governance_position.full_clean()
    governance_position.save()

    return (organization_slug, governance_body_name, name), governance_position
