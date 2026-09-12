from rest_framework import serializers

MAX_MESSAGE_LENGTH = 4_000


class MessageField(serializers.CharField):
    """Strict text-only Civic Assistant message."""

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError("Expected text.")
        return super().to_internal_value(data)


class CivicAssistantRequestSerializer(serializers.Serializer):
    """Validate the bounded Civic Assistant request body."""

    message = MessageField(
        max_length=MAX_MESSAGE_LENGTH,
        allow_blank=False,
        trim_whitespace=True,
    )

    def to_internal_value(self, data):
        if not isinstance(data, dict) or set(data) != {"message"}:
            raise serializers.ValidationError({"message": "Expected only a message field."})

        return super().to_internal_value(data)
