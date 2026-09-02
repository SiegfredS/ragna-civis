from datetime import date

import pytest

from apps.organizations.tests.factories import OrganizationFactory
from apps.projects.choices import ProjectStatus
from apps.projects.models import Project
from apps.utils.bootstrap.utils.projects.create_projects import create_projects


@pytest.mark.django_db
class TestCreateProjects:
    def test_creates_and_updates_project_with_dates(self):
        organization = OrganizationFactory(slug="civic-hall")
        data = {
            "organization": organization.slug,
            "title": "Market Renewal",
            "slug": "market-renewal",
            "description": "Original",
            "status": ProjectStatus.PLANNED,
            "start_date": "2026-01-01",
            "end_date": None,
        }

        create_projects([data])
        create_projects([{**data, "title": "Updated Market Renewal", "status": ProjectStatus.ACTIVE}])

        project = Project.objects.get(organization=organization, slug="market-renewal")

        assert project.title == "Updated Market Renewal"
        assert project.status == ProjectStatus.ACTIVE
        assert project.start_date == date(2026, 1, 1)
        assert project.end_date is None
        assert Project.objects.filter(organization=organization, slug=project.slug).count() == 1

    def test_rejects_missing_organization_and_invalid_status(self):
        data = {"organization": "missing", "title": "Project", "slug": "project", "status": ProjectStatus.DRAFT}
        with pytest.raises(ValueError, match="does not exist"):
            create_projects([data])

        organization = OrganizationFactory(slug="civic-hall")
        with pytest.raises(ValueError, match="Invalid project status"):
            create_projects(
                [{"organization": organization.slug, "title": "Project", "slug": "project", "status": "invalid"}]
            )
