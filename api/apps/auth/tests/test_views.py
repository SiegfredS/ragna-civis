from typing import cast

import pytest
from django.test import override_settings
from knox.models import AuthToken  # type: ignore[import-untyped]

from apps.auth.endpoints import LOGIN_URL, LOGOUT_ALL_URL, LOGOUT_URL, REGISTER_URL
from apps.profiles.endpoints import CURRENT_USER_PROFILE_URL
from apps.profiles.models import UserProfile
from apps.testing import APIClient
from apps.users.models import User


@pytest.mark.django_db
class TestRegisterView:
    url = REGISTER_URL

    def test_register_creates_user_and_returns_token_with_user(self, api_client: APIClient) -> None:
        response = api_client.post(
            self.url,
            data={
                "username": "new-user",
                "email": "new-user@example.com",
                "password": "uncommon-register-password-123",
                "firstName": "New",
                "middleName": "",
                "lastName": "User",
            },
            format="json",
        )

        assert response.status_code == 200
        assert User.objects.filter(username="new-user").exists()
        user = User.objects.get(username="new-user")
        assert UserProfile.objects.filter(user=user).exists()
        assert user.check_password("uncommon-register-password-123")
        assert response.json()["user"] == {
            "id": user.pk,
            "username": "new-user",
            "email": "new-user@example.com",
            "firstName": "New",
            "middleName": "",
            "lastName": "User",
        }
        assert response.json()["token"]
        assert response.json()["expiry"]

        profile_response = api_client.get(
            CURRENT_USER_PROFILE_URL,
            HTTP_AUTHORIZATION=f"Token {response.json()['token']}",
        )

        assert profile_response.status_code == 200
        assert profile_response.json() == {
            "id": user.pk,
            "username": "new-user",
            "email": "new-user@example.com",
            "firstName": "New",
            "middleName": "",
            "lastName": "User",
            "avatar": None,
        }


@pytest.mark.django_db
class TestLoginView:
    url = LOGIN_URL

    @override_settings(CORS_ALLOWED_ORIGINS=["http://localhost:3000"])
    def test_allows_the_web_origin_to_send_a_login_post(self, api_client: APIClient) -> None:
        response = api_client.options(
            self.url,
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

        assert response.status_code == 200
        assert response["Access-Control-Allow-Origin"] == "http://localhost:3000"
        assert "POST" in response["Access-Control-Allow-Methods"]

    @override_settings(CORS_ALLOWED_ORIGINS=["http://localhost:3000"])
    def test_rejects_an_unconfigured_web_origin(self, api_client: APIClient) -> None:
        response = api_client.options(
            self.url,
            HTTP_ORIGIN="https://untrusted.example",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

        assert response.status_code == 200
        assert not response.has_header("Access-Control-Allow-Origin")

    def test_login_returns_token_and_user(self, user: User, api_client: APIClient) -> None:
        response = api_client.post(
            self.url,
            data={"username": user.username, "password": "test-password"},
            format="json",
        )

        assert response.status_code == 200
        assert response.json()["token"]
        assert response.json()["user"] == {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "firstName": user.first_name,
            "middleName": user.middle_name,
            "lastName": user.last_name,
        }

    def test_login_accepts_email_case_insensitively(self, user: User, api_client: APIClient) -> None:
        response = api_client.post(
            self.url,
            data={"username": user.email.upper(), "password": "test-password"},
            format="json",
        )

        assert response.status_code == 200
        assert response.json()["user"]["id"] == user.pk

    def test_login_rejects_invalid_credentials(self, user: User, api_client: APIClient) -> None:
        response = api_client.post(
            self.url,
            data={"username": user.username, "password": "incorrect-password"},
            format="json",
        )

        assert response.status_code == 400
        assert response.json() == {"nonFieldErrors": ["Unable to log in with provided credentials."]}


@pytest.mark.django_db
class TestLogoutView:
    url = LOGOUT_URL

    def test_logout_revokes_only_the_current_token(self, user: User, api_client: APIClient) -> None:
        token_one, raw_token_one = cast(tuple[AuthToken, str], AuthToken.objects.create(user=user))
        token_two, _ = cast(tuple[AuthToken, str], AuthToken.objects.create(user=user))

        response = api_client.post(self.url, HTTP_AUTHORIZATION=f"Token {raw_token_one}")

        assert response.status_code == 204
        assert not AuthToken.objects.filter(pk=token_one.pk).exists()
        assert AuthToken.objects.filter(pk=token_two.pk).exists()


@pytest.mark.django_db
class TestLogoutAllView:
    url = LOGOUT_ALL_URL

    def test_logout_all_revokes_every_user_token(self, user: User, api_client: APIClient) -> None:
        _, raw_token = cast(tuple[AuthToken, str], AuthToken.objects.create(user=user))
        AuthToken.objects.create(user=user)

        response = api_client.post(self.url, HTTP_AUTHORIZATION=f"Token {raw_token}")

        assert response.status_code == 204
        assert not AuthToken.objects.filter(user=user).exists()
