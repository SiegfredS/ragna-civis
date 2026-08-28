from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    avatar = models.ImageField(_("avatar"), upload_to="user_profiles/avatars/", blank=True, null=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self) -> str:
        return str(self.user)
