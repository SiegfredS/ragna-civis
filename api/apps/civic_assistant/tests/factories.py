from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.civic_assistant.choices import PromptType
from apps.civic_assistant.models import Prompt, PromptGroup, PromptGroupPrompt


class PromptFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Prompt

    key = Sequence(lambda number: f"prompt-{number}")
    prompt_type = PromptType.SYSTEM
    content = "Test prompt content."


class PromptGroupFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = PromptGroup

    key = Sequence(lambda number: f"prompt-group-{number}")


class PromptGroupPromptFactory(DjangoModelFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = PromptGroupPrompt

    prompt_group = SubFactory(PromptGroupFactory)
    prompt = SubFactory(PromptFactory)
    ordering_index = Sequence(lambda number: number)
