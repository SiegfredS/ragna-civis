from factory.declarations import SelfAttribute, Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.governance.choices import GovernanceBodyType
from apps.governance.models import GovernanceBody, GovernancePosition, GovernancePositionAssignment
from apps.organizations.tests.factories import OrganizationFactory, OrganizationMembershipFactory


class GovernanceBodyFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = GovernanceBody

    organization = SubFactory(OrganizationFactory)
    name = Sequence(lambda n: f"Governance Body {n}")
    body_type = GovernanceBodyType.COUNCIL


class GovernancePositionFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = GovernancePosition

    governance_body = SubFactory(GovernanceBodyFactory)
    name = Sequence(lambda n: f"Position {n}")


class GovernancePositionAssignmentFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = GovernancePositionAssignment

    membership = SubFactory(OrganizationMembershipFactory)
    position = SubFactory(
        GovernancePositionFactory,
        governance_body__organization=SelfAttribute("...membership.organization"),
    )
