import os

os.environ["OPENAI_API_KEY"] = "test-openai-api-key"
os.environ["OPENAI_MODEL"] = "test-openai-model"
os.environ["DJANGO_LOG_LEVEL"] = "DEBUG"
os.environ["CIVIC_ASSISTANT_MODEL_TIMEOUT_SECONDS"] = "30"
os.environ["CIVIC_ASSISTANT_MODEL_MAX_COMPLETION_TOKENS"] = "1024"

from .base import *  # noqa: F403

# Keep tests deterministic when CI supplies a production-style DJANGO_DEBUG value.
DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ENVIRONMENT = "test"
