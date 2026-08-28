from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    # for third party implementation, look at:
    # https://django-model-utils.readthedocs.io/en/3.1.2/models.html#timestampedmodel
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_("Modified"))

    class Meta:
        abstract = True


class DatePeriodModel(models.Model):
    """Abstract model representing an optional inclusive date period."""

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                condition=(Q(start_date__isnull=True) | Q(end_date__isnull=True) | Q(end_date__gte=F("start_date"))),
                name="%(app_label)s_%(class)s_valid_date_period",
            ),
        ]
