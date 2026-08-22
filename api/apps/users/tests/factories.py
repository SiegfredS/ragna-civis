from django.contrib.auth.hashers import make_password
from factory.declarations import Sequence
from factory.django import DjangoModelFactory

from apps.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = User

    username = Sequence(lambda n: f"user{n}")
    first_name = "Test"
    middle_name = ""
    last_name = "User"
    email = Sequence(lambda n: f"user{n}@example.com")
    password = make_password("test-password")
