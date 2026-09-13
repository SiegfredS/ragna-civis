import pytest

from apps.organizations.queries.overview import (
    ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH,
    OrganizationOverviewCallerUnavailableError,
    read_organization_overview,
)
from apps.organizations.tests.factories import OrganizationFactory
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestReadOrganizationOverview:
    def test_returns_the_allowlisted_organization_overview(self, user, organization):
        result = read_organization_overview(
            caller_user_id=user.pk,
            identifier=organization.slug,
        )

        assert result == {
            "status": "ok",
            "slug": organization.slug,
            "name": organization.name,
            "description": organization.description,
            "organization_type": organization.organization_type,
            "description_truncated": False,
        }
        assert set(result) == {
            "status",
            "slug",
            "name",
            "description",
            "organization_type",
            "description_truncated",
        }

    def test_raises_when_caller_is_missing(self, organization):
        with pytest.raises(OrganizationOverviewCallerUnavailableError):
            read_organization_overview(caller_user_id=None, identifier=organization.slug)

    def test_raises_when_caller_user_does_not_exist(self, organization):
        with pytest.raises(OrganizationOverviewCallerUnavailableError):
            read_organization_overview(caller_user_id=0, identifier=organization.slug)

    def test_raises_when_caller_is_inactive(self, organization):
        user = UserFactory(is_active=False)

        with pytest.raises(OrganizationOverviewCallerUnavailableError):
            read_organization_overview(caller_user_id=user.pk, identifier=organization.slug)

    def test_returns_not_found_when_an_organization_does_not_exist(self, user):
        assert read_organization_overview(caller_user_id=user.pk, identifier="missing-organization") == {
            "status": "not_found"
        }

    def test_resolves_an_exact_case_insensitive_name(self, user):
        organization = OrganizationFactory(name="Liyue Qixing", slug="liyue-qixing")

        result = read_organization_overview(caller_user_id=user.pk, identifier="LIYUE QIXING")

        assert result["slug"] == organization.slug

    def test_resolves_a_unique_case_insensitive_partial_name(self, user):
        organization = OrganizationFactory(name="Liyue Qixing", slug="liyue-qixing")

        result = read_organization_overview(caller_user_id=user.pk, identifier="liyue")

        assert result["slug"] == organization.slug

    def test_prefers_an_exact_slug_over_an_exact_name(self, user):
        slug_match = OrganizationFactory(name="Other Organization", slug="liyue")
        OrganizationFactory(name="Liyue", slug="liyue-qixing")

        result = read_organization_overview(caller_user_id=user.pk, identifier="LIYUE")

        assert result["slug"] == slug_match.slug

    def test_returns_ambiguous_for_multiple_partial_name_matches(self, user):
        OrganizationFactory(name="Liyue Qixing", slug="liyue-qixing")
        OrganizationFactory(name="Liyue Harbor", slug="liyue-harbor")

        assert read_organization_overview(caller_user_id=user.pk, identifier="liyue") == {"status": "ambiguous"}

    def test_does_not_require_membership(self, user, organization):
        result = read_organization_overview(
            caller_user_id=user.pk,
            identifier=organization.slug,
        )

        assert result["slug"] == organization.slug

    def test_preserves_a_description_below_the_limit(self, user):
        description = "short description"
        organization = OrganizationFactory(description=description)

        result = read_organization_overview(caller_user_id=user.pk, identifier=organization.slug)

        assert result["description"] == description
        assert result["description_truncated"] is False

    def test_preserves_a_description_at_the_limit(self, user):
        description = "a" * ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH
        organization = OrganizationFactory(description=description)

        result = read_organization_overview(caller_user_id=user.pk, identifier=organization.slug)

        assert result["description"] == description
        assert result["description_truncated"] is False

    def test_truncates_a_description_over_the_limit(self, user):
        description = "a" * (ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH + 1)
        organization = OrganizationFactory(description=description)

        result = read_organization_overview(caller_user_id=user.pk, identifier=organization.slug)

        assert result["description"] == description[:ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH]
        assert len(result["description"]) == ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH
        assert result["description_truncated"] is True
