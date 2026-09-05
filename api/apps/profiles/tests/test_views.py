from typing import cast

import pytest
from knox.models import AuthToken  # type: ignore[import-untyped]

from apps.profiles.endpoints import CURRENT_USER_PROFILE_URL
from apps.profiles.models import UserProfile
from apps.profiles.serializers import UserProfileSerializer
from apps.testing import APIClient


@pytest.mark.django_db
class TestCurrentUserProfileView:
    url = CURRENT_USER_PROFILE_URL

    def test_rejects_unauthenticated_requests(self, api_client: APIClient) -> None:
        response = api_client.get(self.url)

        assert response.status_code == 401

    def test_authenticates_a_knox_token_and_returns_camel_case_json(
        self, user_profile: UserProfile, api_client: APIClient
    ) -> None:
        _, token = cast(tuple[AuthToken, str], AuthToken.objects.create(user=user_profile.user))

        response = api_client.get(self.url, HTTP_AUTHORIZATION=f"Token {token}")

        assert response.status_code == 200
        assert response.json() == {
            "id": user_profile.user.id,
            "username": user_profile.user.username,
            "email": user_profile.user.email,
            "firstName": user_profile.user.first_name,
            "middleName": user_profile.user.middle_name,
            "lastName": user_profile.user.last_name,
            "avatar": None,
        }

    def test_serializer_fields_remain_snake_case(self, user_profile: UserProfile) -> None:
        serializer = UserProfileSerializer(user_profile)

        assert set(serializer.data) == {
            "id",
            "username",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "avatar",
        }
