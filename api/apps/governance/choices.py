from django.db import models
from django.utils.translation import gettext_lazy as _


class GovernanceBodyType(models.TextChoices):
    EXECUTIVE = "executive", _("Executive")
    BOARD = "board", _("Board")
    COUNCIL = "council", _("Council")
    COMMITTEE = "committee", _("Committee")
    ADVISORY = "advisory", _("Advisory")
    OTHER = "other", _("Other")
