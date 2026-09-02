import pytest

from apps.users.tests.factories import UserFactory
from apps.utils.bootstrap.utils.lookups.user_profiles import get_user_profile


@pytest.mark.django_db
class TestGetUserProfile:
    def test_resolves_by_username(self):
        user = UserFactory(username="alice")

        assert get_user_profile(username="alice").user == user

    def test_rejects_missing_user_profile(self):
        with pytest.raises(ValueError, match="user profile for username 'missing' does not exist"):
            get_user_profile(username="missing")
