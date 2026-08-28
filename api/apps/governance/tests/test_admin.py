import pytest
from django.contrib import admin
from django.test import RequestFactory

from apps.governance.admin import GovernancePositionAssignmentAdmin
from apps.governance.models import GovernancePositionAssignment


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
