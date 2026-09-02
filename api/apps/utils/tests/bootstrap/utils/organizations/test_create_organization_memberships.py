import pytest

from apps.organizations.choices import OrganizationMembershipRole
from apps.organizations.models import OrganizationMembership
from apps.organizations.tests.factories import OrganizationFactory, OrganizationMembershipFactory
from apps.users.tests.factories import UserFactory
from apps.utils.bootstrap.utils.organizations.create_organization_memberships import create_organization_memberships


@pytest.mark.django_db
class TestCreateOrganizationMemberships:
    def test_creates_and_updates_membership_without_duplication(self):
        organization = OrganizationFactory(slug="civic-hall")
        user = UserFactory(username="alice")
        data = {"organization": organization.slug, "user": user.username, "role": OrganizationMembershipRole.MEMBER}

        create_organization_memberships([data])
        create_organization_memberships([{**data, "role": OrganizationMembershipRole.ADMIN}])

        membership = OrganizationMembership.objects.get(organization=organization, user_profile__user=user)

        assert membership.role == OrganizationMembershipRole.ADMIN
        assert OrganizationMembership.objects.filter(organization=organization, user_profile__user=user).count() == 1

    def test_rejects_invalid_or_missing_references(self):
        organization = OrganizationFactory(slug="civic-hall")
        user = UserFactory(username="alice")

        with pytest.raises(ValueError, match="Invalid organization membership role"):
            create_organization_memberships(
                [{"organization": organization.slug, "user": user.username, "role": "owner"}]
            )
        with pytest.raises(ValueError, match="does not exist"):
            create_organization_memberships(
                [{"organization": "missing", "user": user.username, "role": OrganizationMembershipRole.MEMBER}]
            )
        with pytest.raises(ValueError, match="does not exist"):
            create_organization_memberships(
                [{"organization": organization.slug, "user": "missing", "role": OrganizationMembershipRole.MEMBER}]
            )

    def test_rejects_ambiguous_existing_membership(self):
        organization = OrganizationFactory(slug="civic-hall")
        user = UserFactory(username="alice")
        OrganizationMembershipFactory(organization=organization, user_profile__user=user)
        OrganizationMembershipFactory(organization=organization, user_profile__user=user)

        with pytest.raises(ValueError, match="Multiple memberships"):
            create_organization_memberships(
                [{"organization": organization.slug, "user": user.username, "role": OrganizationMembershipRole.MEMBER}]
            )
