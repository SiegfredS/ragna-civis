from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.governance.choices import GovernanceBodyType
from apps.organizations.models import Organization, OrganizationMembership
from apps.utils.models import DatePeriodModel, TimeStampedModel
from apps.utils.utils import max_choice_value_length


class GovernanceBody(TimeStampedModel):
    """Formal governing body belonging to an organization."""

    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.PROTECT,
        related_name="governance_bodies",
    )

    name = models.CharField(
        verbose_name=_("name"),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True,
    )
    body_type = models.CharField(
        verbose_name=_("body type"),
        max_length=max_choice_value_length(GovernanceBodyType),
        choices=GovernanceBodyType.choices,
    )

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("Governance Body")
        verbose_name_plural = _("Governance Bodies")
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_governance_body_name_per_organization",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} - ({self.organization})"


class GovernancePosition(TimeStampedModel):
    """position defined within a governance body."""

    governance_body = models.ForeignKey(
        GovernanceBody,
        verbose_name=_("Governance Body"),
        on_delete=models.PROTECT,
        related_name="positions",
    )

    name = models.CharField(
        verbose_name=_("name"),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True,
    )

    class Meta(TimeStampedModel.Meta):
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["governance_body", "name"],
                name="unique_position_name_per_governance_body",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} - ({self.governance_body})"


class GovernancePositionAssignment(TimeStampedModel, DatePeriodModel):
    """Assignment of an organization membership to a governance position."""

    position = models.ForeignKey(
        GovernancePosition,
        verbose_name=_("position"),
        on_delete=models.PROTECT,
        related_name="position_assignments",
    )

    membership = models.ForeignKey(
        OrganizationMembership,
        on_delete=models.CASCADE,
        related_name="position_assignments",
    )

    class Meta(TimeStampedModel.Meta, DatePeriodModel.Meta):
        verbose_name = _("Governance Position Assignment")
        verbose_name_plural = _("Governance Position Assignments")
        ordering = [
            "-start_date",
            "-created",
        ]

    def __str__(self) -> str:
        return f"{self.membership} - {self.position}"

    def clean(self) -> None:
        """Validate that the membership and position share an organization."""
        super().clean()

        if self.position.pk is None or self.membership.pk is None:
            return

        position_organization_id = self.position.governance_body.organization.pk

        if self.membership.organization.pk != position_organization_id:
            raise ValidationError(
                {
                    "membership": ("The membership must belong to the same organization as the governance position."),
                }
            )
