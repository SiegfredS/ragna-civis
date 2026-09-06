import pytest
from django.core.exceptions import ValidationError

from apps.civic_assistant.choices import PromptType
from apps.civic_assistant.models import Prompt
from apps.civic_assistant.tests.factories import PromptFactory
from apps.utils.bootstrap.utils.civic_assistant.create_prompts import create_prompts


def build_prompt_data() -> list[dict[str, str]]:
    return [
        {
            "key": "civic-assistant-system",
            "prompt_type": PromptType.SYSTEM,
            "content": "System prompt content.",
        },
        {
            "key": "civic-assistant-input",
            "prompt_type": PromptType.INPUT_GUARDRAIL,
            "content": "Input guardrail content.",
        },
        {
            "key": "civic-assistant-output",
            "prompt_type": PromptType.OUTPUT_GUARDRAIL,
            "content": "Output guardrail content.",
        },
    ]


@pytest.mark.django_db
class TestCreatePrompts:
    def test_creates_prompts_and_returns_them_keyed_by_key(self):
        data = build_prompt_data()

        prompts = create_prompts(data)

        assert set(prompts) == {prompt_data["key"] for prompt_data in data}
        assert Prompt.objects.count() == len(data)
        for prompt_data in data:
            prompt = prompts[prompt_data["key"]]
            assert prompt.pk is not None
            assert prompt.key == prompt_data["key"]
            assert prompt.prompt_type == prompt_data["prompt_type"]
            assert prompt.content == prompt_data["content"]

    def test_is_idempotent_and_preserves_primary_keys(self):
        data = build_prompt_data()

        first_result = create_prompts(data)
        first_pks = {key: prompt.pk for key, prompt in first_result.items()}

        second_result = create_prompts(data)

        assert Prompt.objects.count() == len(data)
        assert {key: prompt.pk for key, prompt in second_result.items()} == first_pks

    def test_updates_existing_prompt_by_key(self):
        prompt = PromptFactory(
            key="civic-assistant-system",
            prompt_type=PromptType.INPUT_GUARDRAIL,
            content="Stale content.",
        )

        create_prompts(
            [
                {
                    "key": prompt.key,
                    "prompt_type": PromptType.SYSTEM,
                    "content": "Canonical content.",
                }
            ]
        )

        prompt.refresh_from_db()
        assert prompt.prompt_type == PromptType.SYSTEM
        assert prompt.content == "Canonical content."
        assert Prompt.objects.get(key=prompt.key).pk == prompt.pk

    def test_preserves_unrelated_prompt(self):
        unrelated_prompt = PromptFactory(key="unrelated-prompt", content="Keep this content.")

        create_prompts(build_prompt_data())

        unrelated_prompt.refresh_from_db()
        assert unrelated_prompt.content == "Keep this content."
        assert Prompt.objects.filter(pk=unrelated_prompt.pk).exists()

    def test_rejects_duplicate_input_keys(self):
        data = build_prompt_data()
        data.append({**data[0], "content": "Duplicate content."})

        with pytest.raises(ValueError, match="Duplicate bootstrap prompt key"):
            create_prompts(data)

        assert Prompt.objects.count() == 0

    def test_rolls_back_when_a_later_prompt_is_invalid(self):
        data = build_prompt_data()
        data[-1]["prompt_type"] = "invalid"

        with pytest.raises(ValueError, match="Invalid prompt type"):
            create_prompts(data)

        assert Prompt.objects.count() == 0

    def test_rejects_non_list_input(self):
        with pytest.raises(ValueError, match="must be a list"):
            create_prompts({})  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "prompt_data",
        [
            "not a dictionary",
            {"key": "key", "prompt_type": PromptType.SYSTEM},
            {
                "key": "key",
                "prompt_type": PromptType.SYSTEM,
                "content": "content",
                "extra": "field",
            },
        ],
    )
    def test_rejects_invalid_row_shape(self, prompt_data):
        with pytest.raises(ValueError, match="dictionary|exactly"):
            create_prompts([prompt_data])

    @pytest.mark.parametrize("field_name", ["key", "prompt_type", "content"])
    def test_rejects_non_string_field_values(self, field_name):
        prompt_data = build_prompt_data()[0]
        prompt_data[field_name] = 42

        with pytest.raises(ValueError, match=field_name):
            create_prompts([prompt_data])

    def test_rejects_invalid_prompt_type(self):
        prompt_data = build_prompt_data()[0]
        prompt_data["prompt_type"] = "invalid"

        with pytest.raises(ValueError, match="Invalid prompt type"):
            create_prompts([prompt_data])

    def test_rejects_invalid_key(self):
        prompt_data = build_prompt_data()[0]
        prompt_data["key"] = "invalid key"

        with pytest.raises(ValidationError, match="key"):
            create_prompts([prompt_data])

    @pytest.mark.parametrize("content", ["", "   "])
    def test_rejects_blank_content(self, content):
        prompt_data = build_prompt_data()[0]
        prompt_data["content"] = content

        with pytest.raises(ValidationError, match="content"):
            create_prompts([prompt_data])
