import pytest

from apps.governance.choices import GovernanceBodyType
from apps.governance.models import GovernanceBody
from apps.organizations.tests.factories import OrganizationFactory
from apps.utils.bootstrap.utils.governance.create_governance_bodies import create_governance_bodies


@pytest.mark.django_db
class TestCreateGovernanceBodies:
    def test_creates_and_updates_governance_body(self):
        organization = OrganizationFactory(slug="civic-hall")
        data = {
            "organization": organization.slug,
            "name": "Civic Council",
            "description": "Original",
            "body_type": GovernanceBodyType.COUNCIL,
        }

        create_governance_bodies([data])
        create_governance_bodies([{**data, "description": "Updated", "body_type": GovernanceBodyType.BOARD}])

        body = GovernanceBody.objects.get(organization=organization, name="Civic Council")

        assert body.description == "Updated"
        assert body.body_type == GovernanceBodyType.BOARD
        assert GovernanceBody.objects.filter(organization=organization, name=body.name).count() == 1

    def test_rejects_missing_organization_and_invalid_body_type(self):
        with pytest.raises(ValueError, match="does not exist"):
            create_governance_bodies(
                [{"organization": "missing", "name": "Council", "body_type": GovernanceBodyType.COUNCIL}]
            )

        organization = OrganizationFactory(slug="civic-hall")
        with pytest.raises(ValueError, match="Invalid governance body type"):
            create_governance_bodies([{"organization": organization.slug, "name": "Council", "body_type": "invalid"}])
