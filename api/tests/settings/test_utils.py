import logging

import environ
import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings.utils import get_env_with_default, get_required_env


class TestSettingsUtils:
    @pytest.mark.parametrize("name", ["OPENAI_API_KEY", "OPENAI_MODEL"])
    def test_get_required_env_returns_a_trimmed_value(self, monkeypatch, name):
        monkeypatch.setenv(name, "  configured-value  ")

        assert get_required_env(name) == "configured-value"

    @pytest.mark.parametrize("value", ["", "   ", "\t\n"])
    def test_get_required_env_rejects_blank_values(self, monkeypatch, value):
        monkeypatch.setenv("OPENAI_API_KEY", value)

        with pytest.raises(ImproperlyConfigured, match="OPENAI_API_KEY"):
            get_required_env("OPENAI_API_KEY")

    def test_get_required_env_rejects_missing_values(self, monkeypatch):
        monkeypatch.delenv("OPENAI_MODEL", raising=False)

        with pytest.raises(ImproperlyConfigured, match="OPENAI_MODEL"):
            get_required_env("OPENAI_MODEL")

    @pytest.mark.parametrize("value", [None, "", " \t"])
    def test_get_env_with_default_returns_the_default_and_logs_a_warning(self, monkeypatch, caplog, value):
        if value is None:
            monkeypatch.delenv("CIVIC_ASSISTANT_MODEL_TIMEOUT_SECONDS", raising=False)
        else:
            monkeypatch.setenv("CIVIC_ASSISTANT_MODEL_TIMEOUT_SECONDS", value)

        env = environ.Env()

        with caplog.at_level(logging.WARNING, logger="config.settings.utils"):
            result = get_env_with_default(env.int, "CIVIC_ASSISTANT_MODEL_TIMEOUT_SECONDS", 30)

        assert result == 30
        assert "CIVIC_ASSISTANT_MODEL_TIMEOUT_SECONDS" in caplog.text
        assert "using its default" in caplog.text

    def test_get_env_with_default_reads_a_configured_typed_value(self, monkeypatch):
        monkeypatch.setenv("CIVIC_ASSISTANT_MODEL_MAX_COMPLETION_TOKENS", "2048")
        env = environ.Env()

        assert get_env_with_default(env.int, "CIVIC_ASSISTANT_MODEL_MAX_COMPLETION_TOKENS", 1024) == 2048
