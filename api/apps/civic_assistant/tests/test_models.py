import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.civic_assistant.choices import PromptType
from apps.civic_assistant.models import Prompt, PromptGroup, PromptGroupPrompt

from .factories import PromptFactory, PromptGroupFactory, PromptGroupPromptFactory


@pytest.mark.django_db
class TestPromptModel:
    def test_creates_a_prompt(self):
        prompt = PromptFactory()

        assert isinstance(prompt, Prompt)
        assert prompt.pk is not None

    def test_str(self):
        prompt = PromptFactory(key="system")

        assert str(prompt) == prompt.key

    @pytest.mark.parametrize("prompt_type", PromptType.values)
    def test_accepts_valid_prompt_types(self, prompt_type):
        prompt = PromptFactory.build(prompt_type=prompt_type)

        prompt.full_clean()

    def test_rejects_blank_content(self):
        prompt = PromptFactory.build(content="")

        with pytest.raises(ValidationError) as error:
            prompt.full_clean()

        assert "content" in error.value.message_dict

    def test_rejects_whitespace_only_content(self):
        prompt = PromptFactory.build(content=" \t\n")

        with pytest.raises(ValidationError) as error:
            prompt.full_clean()

        assert "content" in error.value.message_dict

    def test_rejects_non_string_content(self):
        prompt = PromptFactory.build(content=None)

        with pytest.raises(ValidationError) as error:
            prompt.full_clean()

        assert "Prompt content cannot be blank" in error.value.message_dict["content"]

    def test_rejects_an_invalid_prompt_type(self):
        prompt = PromptFactory.build(prompt_type="invalid")

        with pytest.raises(ValidationError) as error:
            prompt.full_clean()

        assert "prompt_type" in error.value.message_dict

    def test_requires_unique_keys(self):
        prompt = PromptFactory()

        with pytest.raises(IntegrityError), transaction.atomic():
            PromptFactory(key=prompt.key)


@pytest.mark.django_db
class TestPromptGroupModel:
    def test_creates_a_prompt_group(self):
        prompt_group = PromptGroupFactory()

        assert isinstance(prompt_group, PromptGroup)
        assert prompt_group.pk is not None

    def test_str(self):
        prompt_group = PromptGroupFactory(key="default")

        assert str(prompt_group) == prompt_group.key

    def test_requires_unique_keys(self):
        prompt_group = PromptGroupFactory()

        with pytest.raises(IntegrityError), transaction.atomic():
            PromptGroupFactory(key=prompt_group.key)


@pytest.mark.django_db
class TestPromptGroupPromptModel:
    def test_creates_a_prompt_group_prompt(self):
        prompt_group = PromptGroupFactory()
        prompt = PromptFactory()
        membership = PromptGroupPromptFactory(
            prompt_group=prompt_group,
            prompt=prompt,
            ordering_index=0,
        )

        assert isinstance(membership, PromptGroupPrompt)
        assert membership.pk is not None

    def test_orders_memberships_by_ordering_index(self):
        prompt_group = PromptGroupFactory()
        output_prompt = PromptFactory(key="output")
        system_prompt = PromptFactory(key="system")
        input_prompt = PromptFactory(key="input")

        PromptGroupPromptFactory(prompt_group=prompt_group, prompt=output_prompt, ordering_index=2)
        PromptGroupPromptFactory(prompt_group=prompt_group, prompt=system_prompt, ordering_index=0)
        PromptGroupPromptFactory(prompt_group=prompt_group, prompt=input_prompt, ordering_index=1)

        memberships = prompt_group.memberships.all()

        assert [membership.prompt.key for membership in memberships] == ["system", "input", "output"]

    def test_requires_unique_prompts_per_prompt_group(self):
        membership = PromptGroupPromptFactory(ordering_index=0)

        with pytest.raises(IntegrityError), transaction.atomic():
            PromptGroupPromptFactory(
                prompt_group=membership.prompt_group,
                prompt=membership.prompt,
                ordering_index=1,
            )

    def test_requires_unique_ordering_indexes_per_prompt_group(self):
        membership = PromptGroupPromptFactory(ordering_index=0)

        with pytest.raises(IntegrityError), transaction.atomic():
            PromptGroupPromptFactory(
                prompt_group=membership.prompt_group,
                prompt=PromptFactory(),
                ordering_index=membership.ordering_index,
            )
