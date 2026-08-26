from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.organizations.tests.factories import OrganizationFactory
from apps.projects.choices import ProjectStatus
from apps.projects.models import Project

from .factories import ProjectFactory


@pytest.mark.django_db
class TestProjectModel:
    def test_creates_a_project(self, project):
        assert isinstance(project, Project)
        assert project.pk is not None

    def test_str(self, project):
        assert str(project) == f"{project.title} - ({project.slug})"

    def test_defaults_to_draft_status(self):
        project = Project.objects.create(
            organization=OrganizationFactory(),
            title="New project",
            slug="new-project",
        )

        assert project.status == ProjectStatus.DRAFT

    def test_uses_project_status_choices(self):
        status_field = Project._meta.get_field("status")

        assert status_field.choices == ProjectStatus.choices

    def test_requires_unique_slugs_per_organization(self):
        project = ProjectFactory()

        with pytest.raises(IntegrityError), transaction.atomic():
            ProjectFactory(organization=project.organization, slug=project.slug)

    def test_allows_the_same_slug_in_different_organizations(self):
        first_project = ProjectFactory(slug="public-park")
        second_project = ProjectFactory(slug="public-park", organization=OrganizationFactory())

        assert first_project.organization_id != second_project.organization_id

    def test_allows_dates_to_be_omitted(self):
        project = ProjectFactory()

        assert project.start_date is None
        assert project.end_date is None

    def test_allows_only_a_start_date(self):
        project = ProjectFactory(start_date=date(2026, 1, 1))

        assert project.start_date == date(2026, 1, 1)
        assert project.end_date is None

    def test_allows_a_valid_date_period(self):
        project = ProjectFactory(start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))

        project.full_clean()

        assert project.end_date >= project.start_date

    def test_rejects_an_end_date_before_the_start_date(self):
        project = ProjectFactory.build(start_date=date(2026, 1, 2), end_date=date(2026, 1, 1))

        with pytest.raises(ValidationError):
            project.full_clean()
