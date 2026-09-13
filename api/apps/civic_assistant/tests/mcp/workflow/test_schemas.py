import pytest
from pydantic import ValidationError

from apps.civic_assistant.mcp.workflow.schemas import (
    OrganizationOverviewAmbiguousEvidence,
    OrganizationOverviewEvidence,
    OrganizationOverviewNotFoundEvidence,
    OrganizationOverviewToolArguments,
    organization_overview_result_adapter,
)
from apps.organizations.queries.overview import ORGANIZATION_OVERVIEW_DESCRIPTION_MAX_LENGTH


class TestOrganizationOverviewToolArguments:
    def test_accepts_a_valid_identifier(self):
        result = OrganizationOverviewToolArguments.model_validate({"identifier": "Liyue Qixing"})

        assert result.identifier == "Liyue Qixing"

    @pytest.mark.parametrize("identifier", ["", " ", "a" * 256])
    def test_rejects_invalid_identifier(self, identifier):
        with pytest.raises(ValidationError):
            OrganizationOverviewToolArguments.model_validate({"identifier": identifier})

    def test_rejects_unexpected_fields(self):
        with pytest.raises(ValidationError):
            OrganizationOverviewToolArguments.model_validate({"identifier": "doh", "caller_user_id": 1})


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


class TestOrganizationOverviewResultEvidence:
    def test_accepts_controlled_ambiguous_result(self):
        result = organization_overview_result_adapter.validate_python({"status": "ambiguous"})

        assert isinstance(result, OrganizationOverviewAmbiguousEvidence)

    def test_accepts_controlled_not_found_result(self):
        result = organization_overview_result_adapter.validate_python({"status": "not_found"})

        assert isinstance(result, OrganizationOverviewNotFoundEvidence)
