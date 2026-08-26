from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.organizations.tests.factories import OrganizationFactory
from apps.projects.choices import ProjectStatus
from apps.projects.models import Project


class ProjectFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Project

    organization = SubFactory(OrganizationFactory)
    title = Sequence(lambda n: f"Project {n}")
    slug = Sequence(lambda n: f"project-{n}")
    status = ProjectStatus.DRAFT
