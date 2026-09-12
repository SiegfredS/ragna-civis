from io import BytesIO

import pytest
from rest_framework.exceptions import ParseError

from apps.civic_assistant.utils.parsers import MAX_CHAT_BODY_BYTES, BoundedChatJSONParser, RequestEntityTooLarge


class TestBoundedChatJSONParser:
    def test_parses_a_normal_json_body(self):
        result = BoundedChatJSONParser().parse(BytesIO(b'{"message":"Hello"}'), media_type="application/json")

        assert result == {"message": "Hello"}

    def test_accepts_a_body_exactly_at_the_byte_limit(self):
        body = b" " * (MAX_CHAT_BODY_BYTES - 2) + b"{}"

        assert len(body) == MAX_CHAT_BODY_BYTES
        assert BoundedChatJSONParser().parse(BytesIO(body), media_type="application/json") == {}

    def test_rejects_a_body_over_the_byte_limit_without_truncating(self):
        body = b" " * (MAX_CHAT_BODY_BYTES - 1) + b"{}"

        assert len(body) == MAX_CHAT_BODY_BYTES + 1
        with pytest.raises(RequestEntityTooLarge) as error_info:
            BoundedChatJSONParser().parse(BytesIO(body), media_type="application/json")

        assert error_info.value.status_code == 413

    def test_preserves_normal_malformed_json_errors(self):
        with pytest.raises(ParseError):
            BoundedChatJSONParser().parse(BytesIO(b'{"message":'), media_type="application/json")
