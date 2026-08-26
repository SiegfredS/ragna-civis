from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.organizations.choices import OrganizationType
from apps.organizations.models import Organization, OrganizationMembership
from apps.profiles.tests.factories import UserProfileFactory


class OrganizationFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Organization

    name = Sequence(lambda n: f"Organization {n}")
    slug = Sequence(lambda n: f"organization-{n}")
    organization_type = OrganizationType.CIVIC_ORGANIZATION


class OrganizationMembershipFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = OrganizationMembership

    organization = SubFactory(OrganizationFactory)
    user_profile = SubFactory(UserProfileFactory)
