from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from apps.governance.models import GovernanceBody, GovernancePosition, GovernancePositionAssignment
from apps.organizations.tests.factories import OrganizationFactory, OrganizationMembershipFactory

from .factories import GovernanceBodyFactory, GovernancePositionAssignmentFactory, GovernancePositionFactory


@pytest.mark.django_db
class TestGovernanceBodyModel:
    def test_creates_a_governance_body(self, governance_body):
        assert isinstance(governance_body, GovernanceBody)
        assert governance_body.pk is not None

    def test_belongs_to_an_organization(self, governance_body):
        assert governance_body.organization_id is not None

    def test_str(self, governance_body):
        assert str(governance_body) == f"{governance_body.name} - ({governance_body.organization})"

    def test_requires_unique_names_per_organization(self):
        governance_body = GovernanceBodyFactory()

        with pytest.raises(IntegrityError), transaction.atomic():
            GovernanceBodyFactory(organization=governance_body.organization, name=governance_body.name)

    def test_allows_the_same_name_in_different_organizations(self):
        first_body = GovernanceBodyFactory(name="Council")
        second_body = GovernanceBodyFactory(name="Council", organization=OrganizationFactory())

        assert first_body.organization_id != second_body.organization_id


@pytest.mark.django_db
class TestGovernancePositionModel:
    def test_creates_a_governance_position(self, governance_position):
        assert isinstance(governance_position, GovernancePosition)
        assert governance_position.pk is not None

    def test_belongs_to_a_governance_body(self, governance_position):
        assert governance_position.governance_body_id is not None

    def test_str(self, governance_position):
        assert str(governance_position) == f"{governance_position.name} - ({governance_position.governance_body})"

    def test_requires_unique_names_per_governance_body(self):
        position = GovernancePositionFactory()

        with pytest.raises(IntegrityError), transaction.atomic():
            GovernancePositionFactory(governance_body=position.governance_body, name=position.name)

    def test_allows_the_same_name_in_different_governance_bodies(self):
        first_position = GovernancePositionFactory(name="Chairperson")
        second_position = GovernancePositionFactory(name="Chairperson", governance_body=GovernanceBodyFactory())

        assert first_position.governance_body_id != second_position.governance_body_id

    def test_protects_a_governance_body_with_positions_from_deletion(self):
        position = GovernancePositionFactory()

        with pytest.raises(ProtectedError):
            position.governance_body.delete()


@pytest.mark.django_db
class TestGovernancePositionAssignmentModel:
    def test_creates_an_assignment(self, governance_position_assignment):
        assert isinstance(governance_position_assignment, GovernancePositionAssignment)
        assert governance_position_assignment.pk is not None

    def test_str(self, governance_position_assignment):
        assert str(governance_position_assignment) == (
            f"{governance_position_assignment.membership} - {governance_position_assignment.position}"
        )

    def test_allows_an_assignment_with_matching_organizations(self):
        assignment = GovernancePositionAssignmentFactory()

        assignment.full_clean()

        assert assignment.membership.organization_id == assignment.position.governance_body.organization_id

    def test_rejects_an_assignment_for_different_organizations(self):
        membership = OrganizationMembershipFactory(organization=OrganizationFactory())
        position = GovernancePositionFactory(governance_body=GovernanceBodyFactory(organization=OrganizationFactory()))
        assignment = GovernancePositionAssignmentFactory.build(membership=membership, position=position)

        with pytest.raises(ValidationError) as error:
            assignment.full_clean()

        assert "membership" in error.value.message_dict

    def test_allows_dates_to_be_omitted(self, governance_position_assignment):
        assignment = governance_position_assignment

        assignment.full_clean()

        assert assignment.start_date is None
        assert assignment.end_date is None

    def test_allows_an_open_assignment(self):
        assignment = GovernancePositionAssignmentFactory(end_date=None)

        assert assignment.end_date is None

    def test_allows_a_historical_assignment(self):
        assignment = GovernancePositionAssignmentFactory(start_date=date(2026, 1, 1), end_date=date(2026, 2, 1))

        assignment.full_clean()

        assert assignment.end_date == date(2026, 2, 1)

    def test_rejects_an_end_date_before_the_start_date(self):
        assignment = GovernancePositionAssignmentFactory.build(
            start_date=date(2026, 1, 1),
            end_date=date(2025, 12, 31),
        )

        with pytest.raises(ValidationError):
            assignment.full_clean()

    def test_allows_one_membership_to_hold_multiple_positions(self):
        membership = OrganizationMembershipFactory()
        governance_body = GovernanceBodyFactory(organization=membership.organization)
        first_assignment = GovernancePositionAssignmentFactory(
            membership=membership,
            position=GovernancePositionFactory(governance_body=governance_body),
        )
        second_assignment = GovernancePositionAssignmentFactory(
            membership=membership,
            position=GovernancePositionFactory(governance_body=governance_body),
        )

        assert first_assignment.position_id != second_assignment.position_id

    def test_protects_a_position_with_assignments_from_deletion(self):
        assignment = GovernancePositionAssignmentFactory()

        with pytest.raises(ProtectedError):
            assignment.position.delete()
