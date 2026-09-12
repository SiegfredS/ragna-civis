from django.conf import settings
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from apps.civic_assistant.mcp.workflow.errors import CivicAssistantModelConfigurationError

# No hidden provider retries for one bounded assistant execution.
MODEL_MAX_RETRIES = 0


def build_civic_assistant_chat_model() -> ChatOpenAI:
    """Build the configured Civic Assistant model for one runtime."""
    api_key = settings.OPENAI_API_KEY.strip()
    model_name = settings.OPENAI_MODEL.strip()

    if not api_key:
        raise CivicAssistantModelConfigurationError("OPENAI_API_KEY is not configured.")

    if not model_name:
        raise CivicAssistantModelConfigurationError("OPENAI_MODEL is not configured")

    return ChatOpenAI(
        model=model_name,
        api_key=SecretStr(api_key),
        timeout=settings.CIVIC_ASSISTANT_MODEL_TIMEOUT_SECONDS,
        max_retries=MODEL_MAX_RETRIES,
        max_completion_tokens=settings.CIVIC_ASSISTANT_MODEL_MAX_COMPLETION_TOKENS,
        use_responses_api=True,
    )
