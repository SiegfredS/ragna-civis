import pytest

from apps.organizations.tests.factories import OrganizationMembershipFactory

from .factories import GovernanceBodyFactory, GovernancePositionAssignmentFactory, GovernancePositionFactory


@pytest.fixture
def governance_body(db):
    return GovernanceBodyFactory()


@pytest.fixture
def governance_position(db, governance_body):
    return GovernancePositionFactory(governance_body=governance_body)


@pytest.fixture
def governance_position_assignment(db, governance_position):
    membership = OrganizationMembershipFactory(organization=governance_position.governance_body.organization)
    return GovernancePositionAssignmentFactory(membership=membership, position=governance_position)
