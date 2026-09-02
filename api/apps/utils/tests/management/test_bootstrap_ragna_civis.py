from io import StringIO

import pytest
from django.core.management import call_command

from apps.governance.choices import GovernanceBodyType
from apps.governance.models import GovernanceBody, GovernancePosition, GovernancePositionAssignment
from apps.organizations.choices import OrganizationMembershipRole, OrganizationType
from apps.projects.choices import ProjectStatus
from apps.projects.models import Project
from apps.users.models import User


@pytest.mark.django_db
class TestBootstrapRagnaCivisCommand:
    def test_bootstraps_remaining_sections_in_dependency_order(self, monkeypatch):
        organization = {
            "slug": "civic-hall",
            "name": "Civic Hall",
            "organization_type": OrganizationType.GOVERNMENT_UNIT,
        }
        data = {
            "users": [{"username": "alice", "email": "alice@example.com"}],
            "organizations": [organization],
            "organization_memberships": [
                {"organization": "civic-hall", "user": "alice", "role": OrganizationMembershipRole.MEMBER}
            ],
            "governance_bodies": [
                {"organization": "civic-hall", "name": "Council", "body_type": GovernanceBodyType.COUNCIL}
            ],
            "governance_positions": [{"organization": "civic-hall", "governance_body": "Council", "name": "Chair"}],
            "governance_position_assignments": [
                {
                    "organization": "civic-hall",
                    "governance_body": "Council",
                    "position": "Chair",
                    "user": "alice",
                    "start_date": "2025-01-01",
                    "end_date": None,
                }
            ],
            "projects": [
                {
                    "organization": "civic-hall",
                    "title": "Market Renewal",
                    "slug": "market-renewal",
                    "status": ProjectStatus.ACTIVE,
                }
            ],
        }
        monkeypatch.setattr(
            "apps.utils.management.commands.bootstrap_ragna_civis.load_bootstrap_data",
            lambda **_: data,
        )

        call_command("bootstrap_ragna_civis", stdout=StringIO())

        assert GovernanceBody.objects.count() == 1
        assert GovernancePosition.objects.count() == 1
        assert GovernancePositionAssignment.objects.count() == 1
        assert Project.objects.count() == 1

    def test_dev_flag_is_passed_to_loader(self, monkeypatch):
        calls = []

        def load_data(*, include_dev):
            calls.append(include_dev)
            return {
                "users": [
                    {
                        "username": "admin",
                        "email": "admin@example.com",
                        "password": "admin-password",
                        "is_staff": True,
                        "is_superuser": True,
                    }
                ],
                "organizations": [],
            }

        monkeypatch.setattr("apps.utils.management.commands.bootstrap_ragna_civis.load_bootstrap_data", load_data)

        call_command("bootstrap_ragna_civis", "--dev", stdout=StringIO())

        assert calls == [True]
        admin = User.objects.get(username="admin")
        assert admin.is_staff is True
        assert admin.is_superuser is True
