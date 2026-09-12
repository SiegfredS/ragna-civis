from unittest.mock import Mock

from django.conf import settings
from django.test import override_settings
from pydantic import SecretStr

from apps.civic_assistant import chat_model
from apps.civic_assistant.chat_model import build_civic_assistant_chat_model


class TestBuildCivicAssistantChatModel:
    def test_builds_the_configured_model_without_connecting_to_openai(self, monkeypatch):
        model = Mock()
        chat_openai = Mock(return_value=model)
        monkeypatch.setattr(chat_model, "ChatOpenAI", chat_openai)

        with override_settings(
            OPENAI_API_KEY="  test-api-key  ",
            OPENAI_MODEL="  test-model  ",
            CIVIC_ASSISTANT_MODEL_TIMEOUT_SECONDS=17,
            CIVIC_ASSISTANT_MODEL_MAX_COMPLETION_TOKENS=321,
        ):
            result = build_civic_assistant_chat_model()

            assert result is model
            chat_openai.assert_called_once()
            kwargs = chat_openai.call_args.kwargs
            assert kwargs["model"] == settings.OPENAI_MODEL.strip()
            assert kwargs["api_key"] == SecretStr(settings.OPENAI_API_KEY.strip())
            assert kwargs["timeout"] == 17
            assert kwargs["max_retries"] == 0
            assert kwargs["max_completion_tokens"] == 321
            assert kwargs["use_responses_api"] is True
