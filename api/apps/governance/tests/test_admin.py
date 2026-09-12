import pytest
from django.contrib import admin
from django.test import RequestFactory

from apps.governance.admin import (
    GovernanceBodyAdmin,
    GovernancePositionAdmin,
    GovernancePositionAssignmentAdmin,
    GovernancePositionAssignmentInline,
    GovernancePositionInline,
)
from apps.governance.models import GovernanceBody, GovernancePosition, GovernancePositionAssignment


@pytest.mark.django_db
class TestGovernancePositionAssignmentAdmin:
    def test_searches_by_membership_user_credentials(self, governance_position_assignment):
        model_admin = GovernancePositionAssignmentAdmin(GovernancePositionAssignment, admin.site)
        membership_user = governance_position_assignment.membership.user_profile.user

        for search_term in (membership_user.username, membership_user.email):
            search_results, use_distinct = model_admin.get_search_results(
                RequestFactory().get("/admin/governance/governancepositionassignment/"),
                GovernancePositionAssignment.objects.all(),
                search_term,
            )

            assert list(search_results) == [governance_position_assignment]
            assert use_distinct is False


class TestGovernanceBodyAdmin:
    def test_includes_position_editor(self):
        model_admin = GovernanceBodyAdmin(GovernanceBody, admin.site)

        assert model_admin.inlines == (GovernancePositionInline,)
        assert GovernancePositionInline.model is GovernancePosition
        assert GovernancePositionInline.fk_name == "governance_body"
        assert GovernancePositionInline.fields == ("name",)
        assert GovernancePositionInline.show_change_link is True


class TestGovernancePositionAdmin:
    def test_includes_assignment_editor(self):
        model_admin = GovernancePositionAdmin(GovernancePosition, admin.site)

        assert model_admin.inlines == (GovernancePositionAssignmentInline,)
        assert GovernancePositionAssignmentInline.model is GovernancePositionAssignment
        assert GovernancePositionAssignmentInline.fk_name == "position"
        assert GovernancePositionAssignmentInline.fields == ("membership", "start_date", "end_date")
        assert GovernancePositionAssignmentInline.show_change_link is True
