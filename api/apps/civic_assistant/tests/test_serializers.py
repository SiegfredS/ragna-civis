import pytest

from apps.civic_assistant.serializers import CivicAssistantRequestSerializer


class TestCivicAssistantRequestSerializer:
    def test_accepts_and_trims_a_message(self):
        serializer = CivicAssistantRequestSerializer(data={"message": "  Hello  "})

        assert serializer.is_valid()
        assert serializer.validated_data["message"] == "Hello"

    def test_accepts_a_message_at_the_character_limit(self):
        serializer = CivicAssistantRequestSerializer(data={"message": "x" * 4_000})

        assert serializer.is_valid()
        assert len(serializer.validated_data["message"]) == 4_000

    @pytest.mark.parametrize(
        "data",
        [
            {},
            {"message": "Hello", "extra": "rejected"},
            {"message": ""},
            {"message": " \t\n "},
            {"message": "x" * 4_001},
        ],
        ids=["missing", "extra-field", "blank", "whitespace-only", "too-long"],
    )
    def test_rejects_invalid_message_shapes(self, data):
        serializer = CivicAssistantRequestSerializer(data=data)

        assert not serializer.is_valid()

    @pytest.mark.parametrize("value", [123, 1.5, True, False, None, [], {}])
    def test_rejects_non_string_messages_without_coercion(self, value):
        serializer = CivicAssistantRequestSerializer(data={"message": value})

        assert not serializer.is_valid()
