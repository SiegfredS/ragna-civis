from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import Organization
from apps.projects.choices import ProjectStatus
from apps.utils.models import DatePeriodModel, TimeStampedModel
from apps.utils.utils import max_choice_value_length


class Project(TimeStampedModel, DatePeriodModel):
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.PROTECT,
        related_name="projects",
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
    )
    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
    )

    status = models.CharField(
        max_length=max_choice_value_length(ProjectStatus),
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
        verbose_name=_("status"),
    )

    class Meta(TimeStampedModel.Meta, DatePeriodModel.Meta):
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_project_slug_per_organization",
            ),
            *DatePeriodModel.Meta.constraints,
        ]

    def __str__(self) -> str:
        return f"{self.title} - ({self.slug})"
