from typing import cast

import pytest

from apps.auth.serializers import LoginSerializer, RegisterSerializer
from apps.users.models import User


@pytest.mark.django_db
class TestRegisterSerializer:
    valid_data = {
        "username": "new-user",
        "email": "new-user@example.com",
        "first_name": "New",
        "middle_name": "",
        "last_name": "User",
        "password": "uncommon-register-password-123",
    }

    def test_creates_user_with_a_hashed_password(self) -> None:
        serializer = cast(RegisterSerializer, RegisterSerializer(data=self.valid_data))

        assert serializer.is_valid(), serializer.errors
        user = cast(User, serializer.save())
        assert user.check_password(self.valid_data["password"])

    def test_rejects_case_insensitive_duplicate_username(self, user: User) -> None:
        serializer = cast(
            RegisterSerializer, RegisterSerializer(data={**self.valid_data, "username": user.username.upper()})
        )

        assert not serializer.is_valid()
        assert serializer.errors == {"username": ["A user with that username already exists."]}

    def test_rejects_case_insensitive_duplicate_email(self, user: User) -> None:
        serializer = cast(RegisterSerializer, RegisterSerializer(data={**self.valid_data, "email": user.email.upper()}))

        assert not serializer.is_valid()
        assert serializer.errors == {"email": ["A user with that email already exists."]}

    def test_rejects_password_that_fails_django_validation(self) -> None:
        serializer = cast(RegisterSerializer, RegisterSerializer(data={**self.valid_data, "password": "short"}))

        assert not serializer.is_valid()
        assert "password" in serializer.errors


@pytest.mark.django_db
class TestLoginSerializer:
    def test_authenticates_with_email_case_insensitively(self, user: User) -> None:
        serializer = cast(
            LoginSerializer,
            LoginSerializer(data={"username": user.email.upper(), "password": "test-password"}),
        )

        assert serializer.is_valid(), serializer.errors
        assert serializer.get_authenticated_user() == user

    def test_rejects_invalid_credentials(self, user: User) -> None:
        serializer = cast(
            LoginSerializer,
            LoginSerializer(data={"username": user.username, "password": "incorrect-password"}),
        )

        assert not serializer.is_valid()
        assert serializer.errors == {"non_field_errors": ["Unable to log in with provided credentials."]}
