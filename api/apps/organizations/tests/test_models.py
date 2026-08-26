import pytest
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from apps.organizations.choices import OrganizationMembershipRole, OrganizationType
from apps.organizations.models import Organization, OrganizationMembership
from apps.profiles.tests.factories import UserProfileFactory

from .factories import OrganizationFactory, OrganizationMembershipFactory


@pytest.mark.django_db
class TestOrganizationModel:
    def test_creates_an_organization(self, organization):
        assert isinstance(organization, Organization)
        assert organization.pk is not None
        assert organization.organization_type == OrganizationType.CIVIC_ORGANIZATION

    def test_str(self, organization):
        assert str(organization) == f"{organization.slug}({organization.name})"

    def test_creates_a_parent_child_relationship(self):
        parent = OrganizationFactory()
        child = OrganizationFactory(parent=parent)

        assert child.parent_id == parent.pk
        assert list(parent.children.all()) == [child]

    def test_rejects_a_direct_self_parent(self, organization):
        organization.parent = organization

        with pytest.raises(ValidationError) as error:
            organization.full_clean()

        assert "parent" in error.value.message_dict

    def test_rejects_a_two_node_cycle(self):
        organization = OrganizationFactory()
        child = OrganizationFactory(parent=organization)
        organization.parent = child

        with pytest.raises(ValidationError) as error:
            organization.full_clean()

        assert "parent" in error.value.message_dict

    def test_rejects_a_deeper_cycle(self):
        root = OrganizationFactory()
        child = OrganizationFactory(parent=root)
        grandchild = OrganizationFactory(parent=child)
        root.parent = grandchild

        with pytest.raises(ValidationError) as error:
            root.full_clean()

        assert "parent" in error.value.message_dict

    def test_allows_a_multi_level_hierarchy(self):
        root = OrganizationFactory()
        child = OrganizationFactory(parent=root)
        grandchild = OrganizationFactory(parent=child)

        grandchild.full_clean()

        assert grandchild.parent_id == child.pk
        assert child.parent_id == root.pk

    def test_protects_a_parent_with_children_from_deletion(self):
        parent = OrganizationFactory()
        OrganizationFactory(parent=parent)

        with pytest.raises(ProtectedError):
            parent.delete()


@pytest.mark.django_db
class TestOrganizationMembershipModel:
    def test_creates_a_membership(self, organization_membership):
        assert isinstance(organization_membership, OrganizationMembership)
        assert organization_membership.pk is not None

    def test_str(self, organization_membership):
        assert str(organization_membership) == (
            f"{organization_membership.user_profile} - {organization_membership.organization} "
            f"({organization_membership.role})"
        )

    def test_defaults_to_the_member_role(self):
        membership = OrganizationMembershipFactory()

        assert membership.role == OrganizationMembershipRole.MEMBER

    def test_allows_multiple_memberships_for_an_organization_and_user_profile(self):
        membership = OrganizationMembershipFactory()

        another_membership = OrganizationMembershipFactory(
            organization=membership.organization,
            user_profile=membership.user_profile,
        )

        assert another_membership.user_profile_id == membership.user_profile_id

    def test_allows_different_users_in_the_same_organization(self):
        organization = OrganizationFactory()
        first_membership = OrganizationMembershipFactory(organization=organization)
        second_membership = OrganizationMembershipFactory(organization=organization, user_profile=UserProfileFactory())

        assert first_membership.user_profile_id != second_membership.user_profile_id

    def test_allows_the_same_user_profile_in_different_organizations(self):
        user_profile = UserProfileFactory()
        first_membership = OrganizationMembershipFactory(user_profile=user_profile)
        second_membership = OrganizationMembershipFactory(user_profile=user_profile)

        assert first_membership.organization_id != second_membership.organization_id
