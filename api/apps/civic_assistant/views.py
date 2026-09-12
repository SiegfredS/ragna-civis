from django.db import DatabaseError
from django.http import StreamingHttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from apps.civic_assistant.mcp.workflow.errors import (
    CivicAssistantModelConfigurationError,
    CivicAssistantPromptConfigurationError,
)
from apps.civic_assistant.runtime import prepare_civic_assistant_runtime
from apps.civic_assistant.serializers import CivicAssistantRequestSerializer
from apps.civic_assistant.streaming import stream_civic_assistant_ndjson
from apps.civic_assistant.utils.parsers import BoundedChatJSONParser
from apps.utils.views import ActionSerializerClassMixin


class CivicAssistantUserThrottle(UserRateThrottle):
    """Endpoint-local Civic Assistant request throttle."""

    rate = "10/min"


class CivicAssistantViewSet(  # pyright: ignore[reportIncompatibleMethodOverride]
    ActionSerializerClassMixin,
    viewsets.GenericViewSet,
):
    parser_classes = [BoundedChatJSONParser]
    # DRYPermissions requires a ModelSerializer, while this endpoint intentionally
    # uses a plain strict input serializer with no model-backed write operation.
    permission_classes = [IsAuthenticated]
    throttle_classes = [CivicAssistantUserThrottle]
    action_serializers = {
        ActionSerializerClassMixin.DEFAULT: CivicAssistantRequestSerializer,
        "chat": CivicAssistantRequestSerializer,
    }

    @action(detail=False, methods=["post"], url_path="chat")
    def chat(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            runtime = prepare_civic_assistant_runtime(caller_user_id=request.user.pk)

        except (
            CivicAssistantModelConfigurationError,
            CivicAssistantPromptConfigurationError,
            DatabaseError,
        ):
            return Response(
                {"detail": "The assistant is unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        response = StreamingHttpResponse(
            stream_civic_assistant_ndjson(runtime=runtime, message=serializer.validated_data["message"]),
            content_type="application/x-ndjson",
        )
        response["Cache-Control"] = "no-store"

        return response
