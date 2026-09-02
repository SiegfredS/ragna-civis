import pytest

from apps.profiles.models import UserProfile
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestUserProfileSignals:
    def test_user_profile_is_created_when_user_is_created(self):
        user = UserFactory()

        profile = UserProfile.objects.get(user=user)

        assert profile.user == user
