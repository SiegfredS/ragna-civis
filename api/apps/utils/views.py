from rest_framework import serializers


class ActionSerializerClassMixin:
    """Maps a DRF action name to its serializer class."""

    DEFAULT = "default"
    action: str
    action_serializers: dict[str, type[serializers.Serializer]] = {}

    def get_serializer_class(self) -> type[serializers.Serializer]:
        if self.DEFAULT not in self.action_serializers:
            raise ValueError(f"Default action serializer '{self.DEFAULT}' is missing in action_serializers.")

        return self.action_serializers.get(
            self.action,
            self.action_serializers[self.DEFAULT],
        )
