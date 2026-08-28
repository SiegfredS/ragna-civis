from django.db import models
from django.utils.translation import gettext_lazy as _


class OrganizationType(models.TextChoices):
    GOVERNMENT_UNIT = "government_unit", _("Government Unit")
    GOVERNMENT_AGENCY = "government_agency", _("Government Agency")
    NON_GOVERNMENT_ORGANIZATION = "non_government_organization", _("Non-Government Organization")
    CIVIC_ORGANIZATION = "civic_organization", _("Civic Organization")
    COMMUNITY_GROUP = "community_group", _("Community Group")
    OTHER = "other", _("Other")


class OrganizationMembershipRole(models.TextChoices):
    # Application-level permissions, not real-world positions.
    ADMIN = "admin", _("Admin")
    MEMBER = "member", _("Member")
