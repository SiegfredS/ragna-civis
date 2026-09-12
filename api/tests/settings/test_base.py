import logging

from django.conf import settings


class TestBaseSettings:
    def test_openai_settings_are_configured(self):
        assert settings.OPENAI_API_KEY == "test-openai-api-key"
        assert settings.OPENAI_MODEL == "test-openai-model"

    def test_civic_assistant_settings_use_test_values(self):
        assert settings.CIVIC_ASSISTANT_MODEL_TIMEOUT_SECONDS == 30
        assert settings.CIVIC_ASSISTANT_MODEL_MAX_COMPLETION_TOKENS == 1024

    def test_logging_allows_debug_messages(self):
        assert settings.LOGGING["root"]["level"] == "DEBUG"
        assert logging.getLogger("apps.civic_assistant").isEnabledFor(logging.DEBUG)
