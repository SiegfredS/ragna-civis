from typing import Any

from apps.organizations.models import Organization


def create_organizations(data: list[dict[str, Any]]) -> dict[str, Organization]:
    organizations: dict[str, Organization] = {}

    for organization_data in data:
        organization_slug, organization = create_organization(
            organization_data=organization_data,
            organizations=organizations,
        )
        organizations[organization_slug] = organization

    return organizations


def create_organization(
    organization_data: dict[str, Any], organizations: dict[str, Organization]
) -> tuple[str, Organization]:
    slug = organization_data["slug"]

    parent_slug = organization_data.get("parent")

    if parent_slug and parent_slug not in organizations:
        raise ValueError(f"Organization {slug!r} references unknown parent {parent_slug!r}.")

    parent = organizations[parent_slug] if parent_slug else None
    try:
        organization = Organization.objects.get(slug=slug)
    except Organization.DoesNotExist:
        organization = Organization(slug=slug)
    except Organization.MultipleObjectsReturned as error:
        raise ValueError(f"Bootstrap organization with slug {slug!r} is ambiguous.") from error

    organization.name = organization_data["name"]
    organization.description = organization_data.get("description", "")
    organization.organization_type = organization_data["organization_type"]
    organization.parent = parent

    organization.full_clean()
    organization.save()

    return slug, organization
