from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = models.CharField(max_length=64, verbose_name=_("First Name"))
    middle_name = models.CharField(max_length=64, blank=True, verbose_name=_("Middle Name"))
    last_name = models.CharField(max_length=64, blank=True, verbose_name=_("Last Name"))

    email = models.EmailField(unique=True, verbose_name=_("Email"))
    username = models.CharField(max_length=64, unique=True, verbose_name=_("Username"))
