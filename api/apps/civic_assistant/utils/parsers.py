from io import BytesIO
from typing import Any

from djangorestframework_camel_case.parser import CamelCaseJSONParser  # type: ignore[import-untyped]
from rest_framework.exceptions import APIException

MAX_CHAT_BODY_BYTES = 32 * 1024


class RequestEntityTooLarge(APIException):
    status_code = 413
    default_detail = "Request body is too large."
    default_code = "request_too_large"


class BoundedChatJSONParser(CamelCaseJSONParser):
    """Parse only a bounded Civic Assistant JSON body."""

    def parse(
        self,
        stream,
        media_type: str | None = None,
        parser_context: dict[str, Any] | None = None,
    ):
        body = stream.read(MAX_CHAT_BODY_BYTES + 1)

        if len(body) > MAX_CHAT_BODY_BYTES:
            raise RequestEntityTooLarge()

        return super().parse(
            BytesIO(body),
            media_type=media_type,
            parser_context=parser_context,
        )
