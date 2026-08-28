import pytest

from .factories import OrganizationFactory, OrganizationMembershipFactory


@pytest.fixture
def organization(db):
    return OrganizationFactory()


@pytest.fixture
def organization_membership(db):
    return OrganizationMembershipFactory()
