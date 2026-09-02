from typing import Any

from apps.governance.choices import GovernanceBodyType
from apps.governance.models import GovernanceBody
from apps.utils.bootstrap.utils.lookups.organization import get_organization
from apps.utils.bootstrap.utils.lookups.validators import validate_choice


def create_governance_bodies(data: list[dict[str, Any]]) -> dict[tuple[str, str], GovernanceBody]:
    """Create bootstrap governance bodies keyed by organization slug and name."""
    governance_bodies: dict[tuple[str, str], GovernanceBody] = {}

    for governance_body_data in data:
        identity, governance_body = create_governance_body(data=governance_body_data)
        governance_bodies[identity] = governance_body

    return governance_bodies


def create_governance_body(data: dict[str, Any]) -> tuple[tuple[str, str], GovernanceBody]:
    organization_slug = data["organization"]
    name = data["name"]
    organization = get_organization(slug=organization_slug)

    try:
        governance_body = GovernanceBody.objects.get(organization=organization, name=name)
    except GovernanceBody.DoesNotExist:
        governance_body = GovernanceBody(organization=organization, name=name)
    except GovernanceBody.MultipleObjectsReturned as error:
        raise ValueError(
            f"Multiple governance bodies named {name!r} found in organization {organization_slug!r}."
        ) from error

    governance_body.description = data.get("description", "")
    governance_body.body_type = validate_choice(
        value=data["body_type"],
        choices=GovernanceBodyType,
        field_name="governance body type",
    )
    governance_body.full_clean()
    governance_body.save()

    return (organization_slug, name), governance_body
