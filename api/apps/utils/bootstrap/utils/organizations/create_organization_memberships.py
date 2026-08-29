from typing import Any

from apps.organizations.choices import OrganizationMembershipRole
from apps.organizations.models import OrganizationMembership
from apps.utils.bootstrap.utils.lookups.organization import get_organization
from apps.utils.bootstrap.utils.lookups.user_profiles import get_user_profile
from apps.utils.bootstrap.utils.lookups.validators import validate_choice


def create_organization_memberships(
    data: list[dict[str, Any]],
) -> dict[tuple[str, str], OrganizationMembership]:
    memberships: dict[tuple[str, str], OrganizationMembership] = {}

    for membership_data in data:
        membership_identity, membership = create_organization_membership(data=membership_data)
        memberships[membership_identity] = membership

    return memberships


def create_organization_membership(
    data: dict[str, Any],
) -> tuple[tuple[str, str], OrganizationMembership]:
    username = data["user"]
    organization_slug = data["organization"]
    role = data["role"]

    user_profile = get_user_profile(username=username)
    organization = get_organization(slug=organization_slug)
    role = validate_choice(
        value=role,
        choices=OrganizationMembershipRole,
        field_name="organization membership role",
    )

    memberships = OrganizationMembership.objects.filter(organization=organization, user_profile=user_profile)

    try:
        membership = memberships.get()
    except OrganizationMembership.DoesNotExist:
        membership = None
    except OrganizationMembership.MultipleObjectsReturned as error:
        raise ValueError(
            f"Multiple memberships found for user {username!r} in organization {organization_slug!r}."
        ) from error

    if membership is None:
        membership = OrganizationMembership(
            organization=organization,
            user_profile=user_profile,
        )

    membership.role = role
    membership.full_clean()
    membership.save()

    return (organization_slug, username), membership
