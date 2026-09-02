import pytest

from apps.governance.tests.factories import GovernanceBodyFactory, GovernancePositionFactory
from apps.organizations.tests.factories import OrganizationFactory
from apps.utils.bootstrap.utils.lookups.governance import get_governance_body, get_governance_position


@pytest.mark.django_db
class TestGovernanceLookups:
    def test_resolves_body_and_position_with_organization_scope(self):
        organization = OrganizationFactory(slug="civic-hall")
        body = GovernanceBodyFactory(organization=organization, name="Council")
        position = GovernancePositionFactory(governance_body=body, name="Chair")

        assert get_governance_body(organization_slug="civic-hall", name="Council") == body
        assert (
            get_governance_position(
                organization_slug="civic-hall",
                governance_body_name="Council",
                name="Chair",
            )
            == position
        )

    def test_rejects_missing_or_cross_organization_references(self):
        other_organization = OrganizationFactory(slug="other-hall")
        body = GovernanceBodyFactory(organization=other_organization, name="Council")
        GovernancePositionFactory(governance_body=body, name="Chair")

        with pytest.raises(ValueError, match="governance body.*does not exist"):
            get_governance_body(organization_slug="civic-hall", name="Council")
        with pytest.raises(ValueError, match="governance position.*does not exist"):
            get_governance_position(
                organization_slug="civic-hall",
                governance_body_name="Council",
                name="Chair",
            )
