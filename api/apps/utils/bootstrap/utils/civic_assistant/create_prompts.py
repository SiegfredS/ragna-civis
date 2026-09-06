from typing import Any

from django.db import transaction

from apps.civic_assistant.choices import PromptType
from apps.civic_assistant.models import Prompt
from apps.utils.bootstrap.utils.lookups.validators import validate_choice

_PROMPT_FIELDS = {"key", "prompt_type", "content"}


def create_prompts(data: list[dict[str, Any]]) -> dict[str, Prompt]:
    """Create or update bootstrap prompts keyed by prompt key."""
    if not isinstance(data, list):
        raise ValueError("Bootstrap prompts must be a list.")

    prompts: dict[str, Prompt] = {}
    keys: set[str] = set()

    for index, prompt_data in enumerate(data):
        _validate_prompt_data(prompt_data=prompt_data, index=index)
        key = prompt_data["key"]

        if key in keys:
            raise ValueError(f"Duplicate bootstrap prompt key {key!r}.")
        keys.add(key)

    with transaction.atomic():
        for prompt_data in data:
            key = prompt_data["key"]
            try:
                prompt = Prompt.objects.get(key=key)
            except Prompt.DoesNotExist:
                prompt = Prompt(key=key)
            except Prompt.MultipleObjectsReturned as error:
                raise ValueError(f"Bootstrap prompt with key {key!r} is ambiguous.") from error

            prompt.prompt_type = validate_choice(
                value=prompt_data["prompt_type"],
                choices=PromptType,
                field_name="prompt type",
            )
            prompt.content = prompt_data["content"]
            prompt.full_clean()
            prompt.save()
            prompts[key] = prompt

    return prompts


def _validate_prompt_data(*, prompt_data: Any, index: int) -> None:
    if not isinstance(prompt_data, dict):
        raise ValueError(f"Bootstrap prompt at index {index} must be a dictionary.")

    fields = set(prompt_data)
    if fields != _PROMPT_FIELDS:
        missing_fields = sorted(_PROMPT_FIELDS - fields, key=str)
        extra_fields = sorted(fields - _PROMPT_FIELDS, key=str)
        raise ValueError(
            f"Bootstrap prompt at index {index} must contain exactly key, prompt_type, and content. "
            f"Missing: {missing_fields}; extra: {extra_fields}."
        )

    for field_name in _PROMPT_FIELDS:
        if not isinstance(prompt_data[field_name], str):
            raise ValueError(f"Bootstrap prompt {field_name} at index {index} must be a string.")
