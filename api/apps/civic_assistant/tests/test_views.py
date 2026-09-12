import asyncio
import json
from typing import cast
from unittest.mock import Mock

import pytest
from django.db import DatabaseError
from django.urls import resolve
from knox.models import AuthToken  # type: ignore[import-untyped]
from rest_framework.permissions import AllowAny
from rest_framework.test import APIRequestFactory

from apps.civic_assistant.mcp.workflow.errors import (
    CivicAssistantModelConfigurationError,
    CivicAssistantPromptConfigurationError,
)
from apps.civic_assistant.views import CivicAssistantUserThrottle, CivicAssistantViewSet
from apps.testing import APIClient
from apps.users.models import User

URL = "/api/civic-assistant/chat/"


class FakeRuntime:
    async def stream(self, *, message):
        assert message == "Hello"
        yield {"type": "delta", "text": "Hello"}
        yield {"type": "delta", "text": " world"}


def token_for(user: User) -> str:
    _, token = cast(tuple[AuthToken, str], AuthToken.objects.create(user=user))
    return token


@pytest.mark.django_db
class TestCivicAssistantView:
    def test_resolves_the_expected_chat_route(self):
        match = resolve(URL)

        assert match.url_name == "civic-assistant-chat"

    def test_rejects_anonymous_requests(self, api_client: APIClient):
        response = api_client.post(URL, data={"message": "Hello"}, format="json")

        assert response.status_code == 401

    def test_authenticated_request_prepares_runtime_for_the_authenticated_user(
        self, user: User, api_client: APIClient, monkeypatch
    ):
        token = token_for(user)
        runtime = FakeRuntime()
        prepare_runtime = Mock(return_value=runtime)
        monkeypatch.setattr("apps.civic_assistant.views.prepare_civic_assistant_runtime", prepare_runtime)

        response = api_client.post(
            URL,
            data={"message": "Hello"},
            format="json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )

        assert response.status_code == 200
        assert response["Content-Type"] == "application/x-ndjson"
        assert response["Cache-Control"] == "no-store"
        prepare_runtime.assert_called_once_with(caller_user_id=user.pk)

    @pytest.mark.parametrize(
        "data",
        [
            {},
            {"message": "Hello", "extra": "rejected"},
            {"message": 123},
        ],
        ids=["wrong-shape", "extra-field", "wrong-message-type"],
    )
    def test_invalid_input_does_not_prepare_runtime(self, user: User, api_client: APIClient, monkeypatch, data):
        token = token_for(user)
        prepare_runtime = Mock()
        monkeypatch.setattr("apps.civic_assistant.views.prepare_civic_assistant_runtime", prepare_runtime)

        response = api_client.post(
            URL,
            data=data,
            format="json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )

        assert response.status_code == 400
        prepare_runtime.assert_not_called()

    def test_malformed_json_uses_normal_drf_parse_error(self, user: User, api_client: APIClient):
        response = api_client.post(
            URL,
            data='{"message":',
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_for(user)}",
        )

        assert response.status_code == 400

    def test_unsupported_media_type_returns_415(self, user: User, api_client: APIClient):
        response = api_client.post(
            URL,
            data='{"message":"Hello"}',
            content_type="text/plain",
            HTTP_AUTHORIZATION=f"Token {token_for(user)}",
        )

        assert response.status_code == 415

    def test_oversized_body_returns_413(self, user: User, api_client: APIClient):
        body = b" " * (32 * 1024) + b"{}"

        response = api_client.post(
            URL,
            data=body,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token_for(user)}",
        )

        assert response.status_code == 413

    @pytest.mark.parametrize(
        "error",
        [
            CivicAssistantModelConfigurationError,
            CivicAssistantPromptConfigurationError,
            DatabaseError,
        ],
    )
    def test_preflight_failures_return_generic_503_without_streaming(
        self, user: User, api_client: APIClient, monkeypatch, error
    ):
        monkeypatch.setattr(
            "apps.civic_assistant.views.prepare_civic_assistant_runtime",
            Mock(side_effect=error("sensitive provider and prompt details")),
        )

        response = api_client.post(
            URL,
            data={"message": "Hello"},
            format="json",
            HTTP_AUTHORIZATION=f"Token {token_for(user)}",
        )

        assert response.status_code == 503
        assert response.json() == {"detail": "The assistant is unavailable"}
        assert not getattr(response, "streaming", False)
        assert "sensitive" not in str(response.json())

    def test_user_throttle_is_configured(self):
        assert CivicAssistantViewSet.throttle_classes == [CivicAssistantUserThrottle]
        assert CivicAssistantUserThrottle.rate == "10/min"

    def test_asgi_response_remains_an_async_stream(self, monkeypatch):
        monkeypatch.setattr(CivicAssistantViewSet, "permission_classes", [AllowAny])
        monkeypatch.setattr(
            "apps.civic_assistant.views.prepare_civic_assistant_runtime", Mock(return_value=FakeRuntime())
        )

        request = APIRequestFactory().post(URL, data={"message": "Hello"}, format="json")
        response = CivicAssistantViewSet.as_view({"post": "chat"})(request)

        async def collect_response_chunks():
            return [chunk async for chunk in response.streaming_content]

        chunks = asyncio.run(collect_response_chunks())

        assert response.status_code == 200
        assert response.streaming
        assert response.is_async
        assert len(chunks) == 3
        assert [json.loads(chunk) for chunk in chunks] == [
            {"type": "delta", "text": "Hello"},
            {"type": "delta", "text": " world"},
            {"type": "done"},
        ]
