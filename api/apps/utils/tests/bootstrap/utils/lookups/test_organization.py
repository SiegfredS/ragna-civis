import pytest

from apps.organizations.tests.factories import OrganizationFactory
from apps.utils.bootstrap.utils.lookups.organization import get_organization


@pytest.mark.django_db
class TestGetOrganization:
    def test_resolves_by_slug(self):
        organization = OrganizationFactory(slug="civic-hall")

        assert get_organization(slug="civic-hall") == organization

    def test_rejects_missing_organization(self):
        with pytest.raises(ValueError, match="organization with slug 'missing' does not exist"):
            get_organization(slug="missing")
