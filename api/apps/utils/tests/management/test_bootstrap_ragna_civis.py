from io import StringIO

import pytest
from django.core.management import call_command

from apps.civic_assistant.choices import PromptType
from apps.civic_assistant.models import Prompt, PromptGroup
from apps.governance.choices import GovernanceBodyType
from apps.governance.models import GovernanceBody, GovernancePosition, GovernancePositionAssignment
from apps.organizations.choices import OrganizationMembershipRole, OrganizationType
from apps.projects.choices import ProjectStatus
from apps.projects.models import Project
from apps.users.models import User


@pytest.mark.django_db
class TestBootstrapRagnaCivisCommand:
    def test_bootstraps_prompts_and_is_idempotent(self, monkeypatch):
        data = {
            "prompts": [
                {
                    "key": "civic-assistant-system",
                    "prompt_type": PromptType.SYSTEM,
                    "content": "System prompt content.",
                },
                {
                    "key": "civic-assistant-input",
                    "prompt_type": PromptType.INPUT_GUARDRAIL,
                    "content": "Input guardrail content.",
                },
                {
                    "key": "civic-assistant-output",
                    "prompt_type": PromptType.OUTPUT_GUARDRAIL,
                    "content": "Output guardrail content.",
                },
            ],
            "prompt_groups": [
                {
                    "key": "civic-assistant-selection",
                    "prompts": ["civic-assistant-system", "civic-assistant-input"],
                },
                {
                    "key": "civic-assistant-answer",
                    "prompts": [
                        "civic-assistant-system",
                        "civic-assistant-input",
                        "civic-assistant-output",
                    ],
                },
            ],
        }
        monkeypatch.setattr(
            "apps.utils.management.commands.bootstrap_ragna_civis.load_bootstrap_data",
            lambda **_: data,
        )

        call_command("bootstrap_ragna_civis", stdout=StringIO())
        first_group_pks = dict(PromptGroup.objects.values_list("key", "pk"))
        call_command("bootstrap_ragna_civis", stdout=StringIO())

        assert Prompt.objects.count() == 3
        assert set(Prompt.objects.values_list("key", flat=True)) == {
            "civic-assistant-system",
            "civic-assistant-input",
            "civic-assistant-output",
        }
        assert set(PromptGroup.objects.values_list("key", flat=True)) == {
            "civic-assistant-selection",
            "civic-assistant-answer",
        }
        assert dict(PromptGroup.objects.values_list("key", "pk")) == first_group_pks
        assert list(
            PromptGroup.objects.get(key="civic-assistant-selection")
            .memberships.order_by("ordering_index")
            .values_list("prompt__key", flat=True)
        ) == ["civic-assistant-system", "civic-assistant-input"]
        assert list(
            PromptGroup.objects.get(key="civic-assistant-answer")
            .memberships.order_by("ordering_index")
            .values_list("prompt__key", flat=True)
        ) == ["civic-assistant-system", "civic-assistant-input", "civic-assistant-output"]

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
        assert Prompt.objects.count() == 0

    def test_missing_prompts_section_remains_optional(self, monkeypatch):
        data = {"users": [{"username": "alice", "email": "alice@example.com"}]}
        monkeypatch.setattr(
            "apps.utils.management.commands.bootstrap_ragna_civis.load_bootstrap_data",
            lambda **_: data,
        )

        call_command("bootstrap_ragna_civis", stdout=StringIO())

        assert User.objects.filter(username="alice").exists()
        assert Prompt.objects.count() == 0

    def test_missing_prompt_groups_section_remains_optional(self, monkeypatch):
        data = {
            "prompts": [
                {
                    "key": "civic-assistant-system",
                    "prompt_type": PromptType.SYSTEM,
                    "content": "System prompt content.",
                }
            ]
        }
        monkeypatch.setattr(
            "apps.utils.management.commands.bootstrap_ragna_civis.load_bootstrap_data",
            lambda **_: data,
        )

        call_command("bootstrap_ragna_civis", stdout=StringIO())

        assert Prompt.objects.count() == 1
        assert PromptGroup.objects.count() == 0

    def test_prompt_groups_are_synchronized_on_rerun(self, monkeypatch):
        data = {
            "prompts": [
                {
                    "key": "civic-assistant-system",
                    "prompt_type": PromptType.SYSTEM,
                    "content": "System prompt content.",
                },
                {
                    "key": "civic-assistant-input",
                    "prompt_type": PromptType.INPUT_GUARDRAIL,
                    "content": "Input guardrail content.",
                },
            ],
            "prompt_groups": [
                {
                    "key": "civic-assistant-selection",
                    "prompts": ["civic-assistant-system", "civic-assistant-input"],
                }
            ],
        }
        monkeypatch.setattr(
            "apps.utils.management.commands.bootstrap_ragna_civis.load_bootstrap_data",
            lambda **_: data,
        )

        call_command("bootstrap_ragna_civis", stdout=StringIO())
        prompt_group = PromptGroup.objects.get(key="civic-assistant-selection")
        first_group_pk = prompt_group.pk
        data["prompt_groups"][0]["prompts"] = ["civic-assistant-input"]
        call_command("bootstrap_ragna_civis", stdout=StringIO())

        prompt_group.refresh_from_db()
        assert PromptGroup.objects.count() == 1
        assert prompt_group.pk == first_group_pk
        assert list(prompt_group.memberships.values_list("prompt__key", flat=True)) == ["civic-assistant-input"]

    def test_prompt_failure_rolls_back_earlier_bootstrap_writes(self, monkeypatch):
        data = {
            "users": [{"username": "alice", "email": "alice@example.com"}],
            "prompts": [
                {
                    "key": "civic-assistant-system",
                    "prompt_type": PromptType.SYSTEM,
                    "content": "System prompt content.",
                },
                {
                    "key": "civic-assistant-input",
                    "prompt_type": "invalid",
                    "content": "Input guardrail content.",
                },
            ],
        }
        monkeypatch.setattr(
            "apps.utils.management.commands.bootstrap_ragna_civis.load_bootstrap_data",
            lambda **_: data,
        )

        with pytest.raises(ValueError, match="Invalid prompt type"):
            call_command("bootstrap_ragna_civis", stdout=StringIO())

        assert not User.objects.filter(username="alice").exists()
        assert Prompt.objects.count() == 0

    def test_invalid_prompt_group_rolls_back_earlier_writes_and_prompts(self, monkeypatch):
        data = {
            "users": [{"username": "alice", "email": "alice@example.com"}],
            "prompts": [
                {
                    "key": "civic-assistant-system",
                    "prompt_type": PromptType.SYSTEM,
                    "content": "System prompt content.",
                }
            ],
            "prompt_groups": [
                {
                    "key": "civic-assistant-selection",
                    "prompts": ["missing-prompt"],
                }
            ],
        }
        monkeypatch.setattr(
            "apps.utils.management.commands.bootstrap_ragna_civis.load_bootstrap_data",
            lambda **_: data,
        )

        with pytest.raises(ValueError, match="does not exist"):
            call_command("bootstrap_ragna_civis", stdout=StringIO())

        assert not User.objects.filter(username="alice").exists()
        assert Prompt.objects.count() == 0
        assert PromptGroup.objects.count() == 0

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
