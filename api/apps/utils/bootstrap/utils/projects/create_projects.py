from datetime import date
from typing import Any

from apps.projects.choices import ProjectStatus
from apps.projects.models import Project
from apps.utils.bootstrap.utils.lookups.organization import get_organization
from apps.utils.bootstrap.utils.lookups.validators import validate_choice


def create_projects(data: list[dict[str, Any]]) -> dict[tuple[str, str], Project]:
    """Create bootstrap projects keyed by organization slug and project slug."""
    projects: dict[tuple[str, str], Project] = {}

    for project_data in data:
        identity, project = create_project(data=project_data)
        projects[identity] = project

    return projects


def create_project(data: dict[str, Any]) -> tuple[tuple[str, str], Project]:
    organization_slug = data["organization"]
    slug = data["slug"]
    organization = get_organization(slug=organization_slug)

    try:
        project = Project.objects.get(organization=organization, slug=slug)
    except Project.DoesNotExist:
        project = Project(organization=organization, slug=slug)
    except Project.MultipleObjectsReturned as error:
        raise ValueError(
            f"Multiple projects with slug {slug!r} found in organization {organization_slug!r}."
        ) from error

    project.title = data["title"]
    project.description = data.get("description", "")
    project.status = validate_choice(value=data["status"], choices=ProjectStatus, field_name="project status")
    project.start_date = _parse_date(data.get("start_date"), field_name="start_date")
    project.end_date = _parse_date(data.get("end_date"), field_name="end_date")
    project.full_clean()
    project.save()

    return (organization_slug, slug), project


def _parse_date(value: Any, *, field_name: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError(f"Bootstrap {field_name} must be an ISO date string or null.")

    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Bootstrap {field_name} {value!r} is not a valid ISO date.") from error
