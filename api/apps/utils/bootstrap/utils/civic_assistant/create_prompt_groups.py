from typing import Any

from django.db import transaction

from apps.civic_assistant.models import Prompt, PromptGroup, PromptGroupPrompt
from apps.utils.bootstrap.utils.lookups.civic_assistant import get_prompt

_PROMPT_GROUP_FIELDS = {"key", "prompts"}


def create_prompt_groups(
    data: list[dict[str, Any]],
) -> dict[str, PromptGroup]:
    """Create or synchronize bootstrap prompt groups keyed by group key."""
    validated_groups = _validate_prompt_groups(data=data)
    prompt_groups: dict[str, PromptGroup] = {}

    with transaction.atomic():
        for key, group_prompts in validated_groups:
            try:
                prompt_group = PromptGroup.objects.get(key=key)
            except PromptGroup.DoesNotExist:
                prompt_group = PromptGroup(key=key)
            except PromptGroup.MultipleObjectsReturned as error:
                raise ValueError(f"Bootstrap prompt group with key {key!r} is ambiguous.") from error

            prompt_group.full_clean()
            prompt_group.save()
            prompt_group.memberships.all().delete()  # pyright: ignore[reportAttributeAccessIssue] - Django related_name

            for ordering_index, prompt in enumerate(group_prompts):
                membership = PromptGroupPrompt(
                    prompt_group=prompt_group,
                    prompt=prompt,
                    ordering_index=ordering_index,
                )
                membership.full_clean()
                membership.save()

            prompt_groups[key] = prompt_group

    return prompt_groups


def _validate_prompt_groups(
    *,
    data: Any,
) -> list[tuple[str, list[Prompt]]]:
    if not isinstance(data, list):
        raise ValueError("Bootstrap prompt groups must be a list.")

    validated_groups: list[tuple[str, list[Prompt]]] = []
    group_keys: set[str] = set()

    for index, group_data in enumerate(data):
        _validate_prompt_group_data(group_data=group_data, index=index)
        key = group_data["key"]
        prompt_keys = group_data["prompts"]

        if key in group_keys:
            raise ValueError(f"Duplicate bootstrap prompt group key {key!r}.")
        group_keys.add(key)

        if not prompt_keys:
            raise ValueError(f"Bootstrap prompt group {key!r} must contain at least one prompt.")

        seen_prompt_keys: set[str] = set()
        group_prompts: list[Prompt] = []
        for prompt_index, prompt_key in enumerate(prompt_keys):
            if not isinstance(prompt_key, str):
                raise ValueError(
                    f"Bootstrap prompt reference at index {prompt_index} in group {key!r} must be a string."
                )
            if prompt_key in seen_prompt_keys:
                raise ValueError(f"Duplicate prompt reference {prompt_key!r} in group {key!r}.")
            seen_prompt_keys.add(prompt_key)
            group_prompts.append(get_prompt(key=prompt_key))

        prompt_group = PromptGroup(key=key)
        prompt_group.full_clean(validate_unique=False)
        validated_groups.append((key, group_prompts))

    return validated_groups


def _validate_prompt_group_data(*, group_data: Any, index: int) -> None:
    if not isinstance(group_data, dict):
        raise ValueError(f"Bootstrap prompt group at index {index} must be a dictionary.")

    fields = set(group_data)
    if fields != _PROMPT_GROUP_FIELDS:
        missing_fields = sorted(_PROMPT_GROUP_FIELDS - fields, key=str)
        extra_fields = sorted(fields - _PROMPT_GROUP_FIELDS, key=str)
        raise ValueError(
            f"Bootstrap prompt group at index {index} must contain exactly key and prompts. "
            f"Missing: {missing_fields}; extra: {extra_fields}."
        )

    if not isinstance(group_data["key"], str):
        raise ValueError(f"Bootstrap prompt group key at index {index} must be a string.")
    if not isinstance(group_data["prompts"], list):
        raise ValueError(f"Bootstrap prompt group prompts at index {index} must be a list.")
