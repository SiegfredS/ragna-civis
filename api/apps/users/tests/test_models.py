import pytest
from django.db import IntegrityError

from apps.users.models import User

from .factories import UserFactory


class TestUserModel:
    @pytest.mark.django_db
    def test_user_factory_creates_a_user(self, user):
        assert isinstance(user, User)
        assert user.pk is not None
        assert user.check_password("test-password")

    @pytest.mark.django_db
    def test_user_email_is_unique(self):
        UserFactory(email="same@example.com")

        with pytest.raises(IntegrityError):
            UserFactory(email="same@example.com")
