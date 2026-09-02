import pytest

from apps.organizations.choices import OrganizationType
from apps.organizations.models import Organization
from apps.utils.bootstrap.utils.organizations.create_organizations import create_organizations


@pytest.mark.django_db
class TestCreateOrganizations:
    def test_creates_parent_and_child_and_updates_without_duplication(self):
        create_organizations(
            [
                {"slug": "civic-hall", "name": "Civic Hall", "organization_type": OrganizationType.GOVERNMENT_UNIT},
                {
                    "slug": "public-works",
                    "name": "Public Works",
                    "organization_type": OrganizationType.GOVERNMENT_AGENCY,
                    "parent": "civic-hall",
                },
            ]
        )

        create_organizations(
            [
                {
                    "slug": "civic-hall",
                    "name": "Updated Civic Hall",
                    "description": "Updated",
                    "organization_type": OrganizationType.GOVERNMENT_UNIT,
                }
            ]
        )

        parent = Organization.objects.get(slug="civic-hall")
        child = Organization.objects.get(slug="public-works")

        assert parent.name == "Updated Civic Hall"
        assert parent.description == "Updated"
        assert child.parent == parent
        assert Organization.objects.filter(slug="civic-hall").count() == 1

    def test_rejects_unknown_parent(self):
        with pytest.raises(ValueError, match="unknown parent"):
            create_organizations(
                [
                    {
                        "slug": "public-works",
                        "name": "Public Works",
                        "organization_type": OrganizationType.GOVERNMENT_AGENCY,
                        "parent": "missing",
                    }
                ]
            )
