import pytest

from apps.organizations.queries.overview import (
    ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH,
    OrganizationOverviewCallerUnavailableError,
    OrganizationOverviewNotFoundError,
    read_organization_overview,
)
from apps.organizations.tests.factories import OrganizationFactory
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestReadOrganizationOverview:
    def test_returns_the_allowlisted_organization_overview(self, user, organization):
        result = read_organization_overview(
            caller_user_id=user.pk,
            slug=organization.slug,
        )

        assert result == {
            "slug": organization.slug,
            "name": organization.name,
            "description": organization.description,
            "organization_type": organization.organization_type,
            "description_truncated": False,
        }
        assert set(result) == {
            "slug",
            "name",
            "description",
            "organization_type",
            "description_truncated",
        }

    def test_raises_when_caller_is_missing(self, organization):
        with pytest.raises(OrganizationOverviewCallerUnavailableError):
            read_organization_overview(caller_user_id=None, slug=organization.slug)

    def test_raises_when_caller_user_does_not_exist(self, organization):
        with pytest.raises(OrganizationOverviewCallerUnavailableError):
            read_organization_overview(caller_user_id=0, slug=organization.slug)

    def test_raises_when_caller_is_inactive(self, organization):
        user = UserFactory(is_active=False)

        with pytest.raises(OrganizationOverviewCallerUnavailableError):
            read_organization_overview(caller_user_id=user.pk, slug=organization.slug)

    def test_raises_when_organization_does_not_exist(self, user):
        with pytest.raises(OrganizationOverviewNotFoundError):
            read_organization_overview(caller_user_id=user.pk, slug="missing-organization")

    def test_does_not_require_membership(self, user, organization):
        result = read_organization_overview(
            caller_user_id=user.pk,
            slug=organization.slug,
        )

        assert result["slug"] == organization.slug

    def test_preserves_a_description_below_the_limit(self, user):
        description = "short description"
        organization = OrganizationFactory(description=description)

        result = read_organization_overview(caller_user_id=user.pk, slug=organization.slug)

        assert result["description"] == description
        assert result["description_truncated"] is False

    def test_preserves_a_description_at_the_limit(self, user):
        description = "a" * ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH
        organization = OrganizationFactory(description=description)

        result = read_organization_overview(caller_user_id=user.pk, slug=organization.slug)

        assert result["description"] == description
        assert result["description_truncated"] is False

    def test_truncates_a_description_over_the_limit(self, user):
        description = "a" * (ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH + 1)
        organization = OrganizationFactory(description=description)

        result = read_organization_overview(caller_user_id=user.pk, slug=organization.slug)

        assert result["description"] == description[:ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH]
        assert len(result["description"]) == ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH
        assert result["description_truncated"] is True
