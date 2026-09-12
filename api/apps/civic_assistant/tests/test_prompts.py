from dataclasses import FrozenInstanceError
from typing import cast

import pytest

from apps.civic_assistant.choices import PromptType
from apps.civic_assistant.mcp.workflow.errors import CivicAssistantPromptConfigurationError
from apps.civic_assistant.models import PromptGroup, PromptGroupPrompt
from apps.civic_assistant.prompts import (
    PROMPT_SEPARATOR,
    CivicPromptSnapshot,
    load_civic_prompt_snapshot,
)

from .factories import PromptFactory, PromptGroupFactory, PromptGroupPromptFactory


def create_canonical_prompt_configuration() -> dict[str, PromptGroupPrompt]:
    prompts = {
        "civic-assistant-output": PromptFactory(
            key="civic-assistant-output",
            prompt_type=PromptType.OUTPUT_GUARDRAIL,
            content="Output prompt.",
        ),
        "civic-assistant-input": PromptFactory(
            key="civic-assistant-input",
            prompt_type=PromptType.INPUT_GUARDRAIL,
            content="Input prompt.",
        ),
        "civic-assistant-system": PromptFactory(
            key="civic-assistant-system",
            prompt_type=PromptType.SYSTEM,
            content="System prompt.",
        ),
    }
    selection_group = PromptGroupFactory(key="civic-assistant-selection")
    answer_group = PromptGroupFactory(key="civic-assistant-answer")

    memberships = {
        "selection-input": PromptGroupPromptFactory(
            prompt_group=selection_group,
            prompt=prompts["civic-assistant-input"],
            ordering_index=1,
        ),
        "answer-output": PromptGroupPromptFactory(
            prompt_group=answer_group,
            prompt=prompts["civic-assistant-output"],
            ordering_index=2,
        ),
        "selection-system": PromptGroupPromptFactory(
            prompt_group=selection_group,
            prompt=prompts["civic-assistant-system"],
            ordering_index=0,
        ),
        "answer-input": PromptGroupPromptFactory(
            prompt_group=answer_group,
            prompt=prompts["civic-assistant-input"],
            ordering_index=1,
        ),
        "answer-system": PromptGroupPromptFactory(
            prompt_group=answer_group,
            prompt=prompts["civic-assistant-system"],
            ordering_index=0,
        ),
    }

    return cast(dict[str, PromptGroupPrompt], memberships)


@pytest.mark.django_db
class TestLoadCivicPromptSnapshot:
    def test_composes_canonical_groups_by_ordering_index(self):
        memberships = create_canonical_prompt_configuration()

        snapshot = load_civic_prompt_snapshot()

        assert snapshot.selection == PROMPT_SEPARATOR.join(("System prompt.", "Input prompt."))
        assert snapshot.answer == PROMPT_SEPARATOR.join(("System prompt.", "Input prompt.", "Output prompt."))
        assert memberships["answer-output"].pk is not None

    def test_returns_a_frozen_value_object_without_orm_instances(self):
        create_canonical_prompt_configuration()

        snapshot = load_civic_prompt_snapshot()

        assert type(snapshot) is CivicPromptSnapshot
        assert isinstance(snapshot.selection, str)
        assert isinstance(snapshot.answer, str)
        with pytest.raises(FrozenInstanceError):
            snapshot.selection = "changed"

    def test_fails_closed_when_a_canonical_group_membership_is_missing(self):
        create_canonical_prompt_configuration()
        PromptGroupPrompt.objects.filter(prompt_group__key="civic-assistant-selection").delete()

        with pytest.raises(CivicAssistantPromptConfigurationError, match="invalid composition"):
            load_civic_prompt_snapshot()

    def test_fails_closed_when_a_canonical_group_is_missing_entirely(self):
        create_canonical_prompt_configuration()
        PromptGroup.objects.filter(key="civic-assistant-answer").delete()

        with pytest.raises(CivicAssistantPromptConfigurationError, match="invalid composition"):
            load_civic_prompt_snapshot()

    def test_fails_closed_for_an_extra_membership(self):
        memberships = create_canonical_prompt_configuration()
        extra_prompt = PromptFactory(
            key="civic-assistant-extra",
            prompt_type=PromptType.SYSTEM,
            content="Extra prompt.",
        )
        PromptGroupPromptFactory(
            prompt_group=memberships["selection-system"].prompt_group,
            prompt=extra_prompt,
            ordering_index=2,
        )

        with pytest.raises(CivicAssistantPromptConfigurationError, match="invalid composition"):
            load_civic_prompt_snapshot()

    def test_fails_closed_for_a_wrong_prompt_key(self):
        memberships = create_canonical_prompt_configuration()

        replacement = PromptFactory(
            key="unexpected-prompt",
            prompt_type=PromptType.SYSTEM,
            content="System prompt.",
        )
        memberships["selection-system"].prompt = replacement
        memberships["selection-system"].save(update_fields=["prompt"])

        with pytest.raises(CivicAssistantPromptConfigurationError, match="invalid composition"):
            load_civic_prompt_snapshot()

    def test_fails_closed_for_a_wrong_prompt_type(self):
        memberships = create_canonical_prompt_configuration()
        memberships["selection-system"].prompt.prompt_type = PromptType.OUTPUT_GUARDRAIL
        memberships["selection-system"].prompt.save(update_fields=["prompt_type"])

        with pytest.raises(CivicAssistantPromptConfigurationError, match="invalid composition"):
            load_civic_prompt_snapshot()

    def test_fails_closed_for_wrong_membership_ordering(self):
        memberships = create_canonical_prompt_configuration()
        PromptGroupPrompt.objects.filter(pk=memberships["selection-system"].pk).update(ordering_index=10)
        PromptGroupPrompt.objects.filter(pk=memberships["selection-input"].pk).update(ordering_index=0)
        PromptGroupPrompt.objects.filter(pk=memberships["selection-system"].pk).update(ordering_index=1)

        with pytest.raises(CivicAssistantPromptConfigurationError, match="invalid composition"):
            load_civic_prompt_snapshot()

    def test_fails_closed_for_blank_prompt_content(self):
        memberships = create_canonical_prompt_configuration()
        memberships["selection-system"].prompt.content = " \t\n"
        memberships["selection-system"].prompt.save(update_fields=["content"])

        with pytest.raises(CivicAssistantPromptConfigurationError, match="blank prompt content"):
            load_civic_prompt_snapshot()
