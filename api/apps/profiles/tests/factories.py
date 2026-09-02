from factory.declarations import SubFactory
from factory.django import DjangoModelFactory

from apps.profiles.models import UserProfile
from apps.users.tests.factories import UserFactory


class UserProfileFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = UserProfile
        django_get_or_create = ("user",)

    user = SubFactory(UserFactory)
