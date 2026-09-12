import pytest
from pydantic import ValidationError

from apps.civic_assistant.mcp.workflow.schemas import (
    OrganizationOverviewEvidence,
    OrganizationOverviewToolArguments,
)
from apps.organizations.queries.overview import ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH


class TestOrganizationOverviewToolArguments:
    def test_accepts_a_valid_slug(self):
        result = OrganizationOverviewToolArguments.model_validate({"slug": "doh"})

        assert result.slug == "doh"

    @pytest.mark.parametrize("slug", ["", "a" * 256, "has spaces", "has/slash", "has.dot"])
    def test_rejects_invalid_slug(self, slug):
        with pytest.raises(ValidationError):
            OrganizationOverviewToolArguments.model_validate({"slug": slug})

    def test_rejects_unexpected_fields(self):
        with pytest.raises(ValidationError):
            OrganizationOverviewToolArguments.model_validate({"slug": "doh", "caller_user_id": 1})


class TestOrganizationOverviewEvidence:
    def test_accepts_the_allowlisted_structure(self, organization_payload):
        result = OrganizationOverviewEvidence.model_validate(organization_payload("doh"))

        assert result.model_dump() == organization_payload("doh")

    def test_rejects_missing_required_fields(self, organization_payload):
        payload = organization_payload("doh")
        del payload["organization_type"]

        with pytest.raises(ValidationError):
            OrganizationOverviewEvidence.model_validate(payload)

    def test_rejects_unexpected_fields(self, organization_payload):
        payload = organization_payload("doh")
        payload["internal_id"] = 42

        with pytest.raises(ValidationError):
            OrganizationOverviewEvidence.model_validate(payload)

    def test_rejects_a_description_over_the_bound(self, organization_payload):
        payload = organization_payload("doh")
        payload["description"] = "a" * (ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH + 1)

        with pytest.raises(ValidationError):
            OrganizationOverviewEvidence.model_validate(payload)
