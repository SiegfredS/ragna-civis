import pytest

from apps.governance.models import GovernancePosition
from apps.governance.tests.factories import GovernanceBodyFactory
from apps.organizations.tests.factories import OrganizationFactory
from apps.utils.bootstrap.utils.governance.create_governance_positions import create_governance_positions


@pytest.mark.django_db
class TestCreateGovernancePositions:
    def test_creates_and_updates_position_scoped_to_body_and_organization(self):
        organization = OrganizationFactory(slug="civic-hall")
        other_organization = OrganizationFactory(slug="other-hall")
        body = GovernanceBodyFactory(organization=organization, name="Council")
        GovernanceBodyFactory(organization=other_organization, name="Council")
        data = {
            "organization": organization.slug,
            "governance_body": body.name,
            "name": "Chair",
            "description": "Original",
        }

        create_governance_positions([data])
        create_governance_positions([{**data, "description": "Updated"}])

        position = GovernancePosition.objects.get(governance_body=body, name="Chair")

        assert position.description == "Updated"
        assert GovernancePosition.objects.filter(governance_body=body, name="Chair").count() == 1

    def test_rejects_body_reference_from_another_organization(self):
        organization = OrganizationFactory(slug="civic-hall")
        other_organization = OrganizationFactory(slug="other-hall")
        GovernanceBodyFactory(organization=other_organization, name="Council")

        with pytest.raises(ValueError, match="governance body.*does not exist"):
            create_governance_positions(
                [{"organization": organization.slug, "governance_body": "Council", "name": "Chair"}]
            )
