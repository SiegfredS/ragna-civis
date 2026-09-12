from dataclasses import dataclass

from apps.civic_assistant.choices import PromptType
from apps.civic_assistant.mcp.workflow.errors import CivicAssistantPromptConfigurationError
from apps.civic_assistant.models import PromptGroupPrompt

PROMPT_SEPARATOR = "\n\n"

SELECTION_PROMPT_GROUP_KEY = "civic-assistant-selection"
ANSWER_PROMPT_GROUP_KEY = "civic-assistant-answer"

PROMPT_GROUP_SPECS = {
    SELECTION_PROMPT_GROUP_KEY: (
        (
            "civic-assistant-system",
            PromptType.SYSTEM,
        ),
        (
            "civic-assistant-input",
            PromptType.INPUT_GUARDRAIL,
        ),
    ),
    ANSWER_PROMPT_GROUP_KEY: (
        (
            "civic-assistant-system",
            PromptType.SYSTEM,
        ),
        (
            "civic-assistant-input",
            PromptType.INPUT_GUARDRAIL,
        ),
        (
            "civic-assistant-output",
            PromptType.OUTPUT_GUARDRAIL,
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class CivicPromptSnapshot:
    """Resolved prompts used for one Civic Assistant execution."""

    selection: str
    answer: str


def load_civic_prompt_snapshot() -> CivicPromptSnapshot:
    """Load and validate the canonical Civic Assistant prompt groups."""
    memberships = (
        PromptGroupPrompt.objects.filter(
            prompt_group__key__in=PROMPT_GROUP_SPECS,
        )
        .select_related(
            "prompt_group",
            "prompt",
        )
        .order_by(
            "prompt_group__key",
            "ordering_index",
        )
    )

    memberships_by_group: dict[str, list[PromptGroupPrompt]] = {group_key: [] for group_key in PROMPT_GROUP_SPECS}

    for membership in memberships:
        memberships_by_group[membership.prompt_group.key].append(membership)

    return CivicPromptSnapshot(
        selection=_compose_prompt_group(
            group_key=SELECTION_PROMPT_GROUP_KEY, memberships=memberships_by_group[SELECTION_PROMPT_GROUP_KEY]
        ),
        answer=_compose_prompt_group(
            group_key=ANSWER_PROMPT_GROUP_KEY, memberships=memberships_by_group[ANSWER_PROMPT_GROUP_KEY]
        ),
    )


def _compose_prompt_group(*, group_key: str, memberships: list[PromptGroupPrompt]) -> str:
    expected_prompts = PROMPT_GROUP_SPECS[group_key]
    actual_prompts = tuple(
        (
            membership.prompt.key,
            membership.prompt.prompt_type,
        )
        for membership in memberships
    )

    if actual_prompts != expected_prompts:
        raise CivicAssistantPromptConfigurationError(
            f"Civic Assistant prompt group {group_key!r} has an invalid composition."
        )

    contents: list[str] = []

    for membership in memberships:
        content = membership.prompt.content

        if not content.strip():
            raise CivicAssistantPromptConfigurationError(
                f"Civic Assistant prompt group {group_key!r} contains blank prompt content."
            )

        contents.append(content)

    return PROMPT_SEPARATOR.join(contents)
