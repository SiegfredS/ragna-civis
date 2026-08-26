from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

from apps.organizations.choices import OrganizationMembershipRole, OrganizationType
from apps.profiles.models import UserProfile
from apps.utils.models import TimeStampedModel
from apps.utils.utils import max_choice_value_length


class Organization(TimeStampedModel):
    """Organization participating in the Ragna Civis platform."""

    name = models.CharField(
        verbose_name=_("name"),
        max_length=255,
    )
    slug = models.SlugField(
        verbose_name=_("slug"),
        max_length=255,
        unique=True,
    )
    description = models.TextField(blank=True)

    organization_type = models.CharField(
        verbose_name=_("organization type"),
        max_length=max_choice_value_length(OrganizationType),
        choices=OrganizationType.choices,
    )

    # generic hierarchy
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(
                    id=F("parent_id"),
                ),
                name="organization_cannot_parent_itself",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.slug}({self.name})"

    def clean(self) -> None:
        """Validate that the organization hierarchy contains no cycles."""
        super().clean()

        if self.parent is None:
            return

        # Give a clearer error for the direct A -> A case.
        if self.pk is not None and self.parent.pk == self.pk:
            raise ValidationError(
                {
                    "parent": "An organization cannot be its own parent.",
                },
            )

        ancestor = self.parent or None
        visited_ids: set[int] = set()

        while ancestor is not None:
            # Following the proposed parent chain must never return to self.
            if self.pk is not None and ancestor.pk == self.pk:
                raise ValidationError(
                    {
                        "parent": "This parent would create an organization cycle.",
                    }
                )

            # Prevent validation itself from looping forever if existing
            # database data is already cyclic.
            if ancestor.pk is not None:
                if ancestor.pk in visited_ids:
                    raise ValidationError(
                        {
                            "parent": "The existing organization hierarchy contains a cycle.",
                        }
                    )

                visited_ids.add(ancestor.pk)

            ancestor = ancestor.parent or None


class OrganizationMembership(TimeStampedModel):
    """Application-level membership within an organization."""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user_profile = models.ForeignKey(
        UserProfile,
        verbose_name=_("user profile"),
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )

    role = models.CharField(
        max_length=max_choice_value_length(OrganizationMembershipRole),
        choices=OrganizationMembershipRole.choices,
        default=OrganizationMembershipRole.MEMBER,
    )

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("Organization Membership")
        verbose_name_plural = _("Organization Memberships")

    def __str__(self) -> str:
        return f"{self.user_profile} - {self.organization} ({self.role})"
