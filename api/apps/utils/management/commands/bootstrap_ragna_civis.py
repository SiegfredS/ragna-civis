from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.utils.bootstrap.loader import load_bootstrap_data
from apps.utils.bootstrap.utils.governance.create_governance_bodies import create_governance_bodies
from apps.utils.bootstrap.utils.governance.create_governance_position_assignments import (
    create_governance_position_assignments,
)
from apps.utils.bootstrap.utils.governance.create_governance_positions import create_governance_positions
from apps.utils.bootstrap.utils.organizations.create_organization_memberships import create_organization_memberships
from apps.utils.bootstrap.utils.organizations.create_organizations import create_organizations
from apps.utils.bootstrap.utils.projects.create_projects import create_projects
from apps.utils.bootstrap.utils.users.create_users import create_users


class Command(BaseCommand):
    help = "Bootstrap Ragna Civis with realistic local development data."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dev",
            action="store_true",
            help="Include development-only data such as local superusers.",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        include_dev = options["dev"]

        if include_dev:
            self.stdout.write(
                self.style.WARNING(
                    "Ragna Civis bootstrap `--dev` flag is ON, this might include data that are only for development "
                    "(i.e admin users)"
                )
            )

        data = load_bootstrap_data(
            include_dev=include_dev,
        )

        self._create_users(data)
        self._create_organizations(data)
        self._create_organization_memberships(data)
        self._create_governance_bodies(data)
        self._create_governance_positions(data)
        self._create_governance_position_assignments(data)
        self._create_projects(data)

        self.stdout.write(
            self.style.SUCCESS("Ragna Civis bootstrap completed successfully."),
        )

    def _create_users(self, data: dict[str, Any]) -> None:
        users_data = data.get("users", [])

        with self._bootstrap_step("users"):
            create_users(users_data)

    def _create_organizations(self, data: dict[str, Any]) -> None:
        organization_data = data.get("organizations", [])

        with self._bootstrap_step("organizations"):
            create_organizations(organization_data)

    def _create_organization_memberships(self, data: dict[str, Any]) -> None:
        organization_membership_data = data.get("organization_memberships", [])

        with self._bootstrap_step("organization memberships"):
            create_organization_memberships(organization_membership_data)

    def _create_governance_bodies(self, data: dict[str, Any]) -> None:
        governance_body_data = data.get("governance_bodies", [])

        with self._bootstrap_step("governance bodies"):
            create_governance_bodies(governance_body_data)

    def _create_governance_positions(self, data: dict[str, Any]) -> None:
        governance_position_data = data.get("governance_positions", [])

        with self._bootstrap_step("governance positions"):
            create_governance_positions(governance_position_data)

    def _create_governance_position_assignments(self, data: dict[str, Any]) -> None:
        assignment_data = data.get("governance_position_assignments", [])

        with self._bootstrap_step("governance position assignments"):
            create_governance_position_assignments(assignment_data)

    def _create_projects(self, data: dict[str, Any]) -> None:
        project_data = data.get("projects", [])

        with self._bootstrap_step("projects"):
            create_projects(project_data)

    @contextmanager
    def _bootstrap_step(self, name: str) -> Generator[None, None, None]:
        """Write consistent progress messages around a bootstrap step."""
        self.stdout.write(f"Creating {name}...")

        yield

        self.stdout.write(
            self.style.SUCCESS(f"Created {name}."),
        )
