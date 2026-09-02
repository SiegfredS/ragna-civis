from datetime import date

import pytest

from apps.governance.models import GovernancePositionAssignment
from apps.governance.tests.factories import GovernanceBodyFactory, GovernancePositionFactory
from apps.organizations.tests.factories import OrganizationFactory, OrganizationMembershipFactory
from apps.users.tests.factories import UserFactory
from apps.utils.bootstrap.utils.governance.create_governance_position_assignments import (
    create_governance_position_assignments,
)


@pytest.mark.django_db
class TestCreateGovernancePositionAssignments:
    def setup_method(self):
        self.organization = OrganizationFactory(slug="civic-hall")
        self.user = UserFactory(username="alice")
        self.body = GovernanceBodyFactory(organization=self.organization, name="Council")
        self.position = GovernancePositionFactory(governance_body=self.body, name="Chair")
        self.membership = OrganizationMembershipFactory(
            organization=self.organization,
            user_profile__user=self.user,
        )

    def assignment_data(self, **overrides):
        return {
            "organization": self.organization.slug,
            "governance_body": self.body.name,
            "position": self.position.name,
            "user": self.user.username,
            "start_date": "2025-01-01",
            "end_date": None,
            **overrides,
        }

    def test_creates_open_assignment_and_is_idempotent(self):
        data = self.assignment_data()

        create_governance_position_assignments([data])
        create_governance_position_assignments([data])

        assignment = GovernancePositionAssignment.objects.get()

        assert assignment.membership == self.membership
        assert assignment.start_date == date(2025, 1, 1)
        assert assignment.end_date is None
        assert GovernancePositionAssignment.objects.count() == 1

    def test_preserves_distinct_historical_periods(self):
        create_governance_position_assignments([self.assignment_data(end_date="2025-06-30")])
        create_governance_position_assignments([self.assignment_data(start_date="2025-07-01")])

        assert GovernancePositionAssignment.objects.count() == 2

    def test_rejects_missing_membership_reference(self):
        self.membership.delete()

        with pytest.raises(ValueError, match="membership.*does not exist"):
            create_governance_position_assignments([self.assignment_data()])
