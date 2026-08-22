from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    # for third party implementation, look at:
    # https://django-model-utils.readthedocs.io/en/3.1.2/models.html#timestampedmodel
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_("Modified"))

    class Meta:
        abstract = True
