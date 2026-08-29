import pytest

from apps.profiles.models import UserProfile
from apps.users.models import User
from apps.users.tests.factories import UserFactory
from apps.utils.bootstrap.utils.users.create_users import create_users


@pytest.mark.django_db
class TestCreateUsers:
    def test_creates_user_with_default_password_and_profile(self):
        create_users([{"username": "alice", "email": "alice@example.com"}])

        user = User.objects.get(username="alice")

        assert user.check_password("ragna-civis")
        assert UserProfile.objects.filter(user=user).exists()

    def test_respects_explicit_password_and_development_flags(self):
        create_users(
            [
                {
                    "username": "admin",
                    "email": "admin@example.com",
                    "password": "custom-password",
                    "is_staff": True,
                    "is_superuser": True,
                }
            ]
        )

        user = User.objects.get(username="admin")

        assert user.check_password("custom-password")
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_updates_existing_user_without_duplication(self):
        UserFactory(username="alice", email="old@example.com", first_name="Old")

        create_users(
            [
                {
                    "username": "alice",
                    "email": "new@example.com",
                    "first_name": "New",
                    "middle_name": "Middle",
                    "password": "new-password",
                }
            ]
        )

        user = User.objects.get(username="alice")

        assert User.objects.filter(username="alice").count() == 1
        assert user.email == "new@example.com"
        assert user.first_name == "New"
        assert user.middle_name == "Middle"
        assert user.check_password("new-password")
