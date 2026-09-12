import pytest
from django.core.exceptions import ValidationError

from apps.civic_assistant.models import Prompt, PromptGroup, PromptGroupPrompt
from apps.civic_assistant.tests.factories import PromptFactory, PromptGroupFactory, PromptGroupPromptFactory
from apps.utils.bootstrap.utils.civic_assistant.create_prompt_groups import create_prompt_groups
from apps.utils.bootstrap.utils.civic_assistant.create_prompts import create_prompts


def build_prompts() -> dict[str, Prompt]:
    return create_prompts(
        [
            {
                "key": "civic-assistant-system",
                "prompt_type": "system",
                "content": "System prompt content.",
            },
            {
                "key": "civic-assistant-input",
                "prompt_type": "input_guardrail",
                "content": "Input guardrail content.",
            },
            {
                "key": "civic-assistant-output",
                "prompt_type": "output_guardrail",
                "content": "Output guardrail content.",
            },
        ]
    )


def build_group_data() -> list[dict[str, object]]:
    return [
        {
            "key": "civic-assistant-selection",
            "prompts": ["civic-assistant-system", "civic-assistant-input"],
        },
        {
            "key": "civic-assistant-answer",
            "prompts": [
                "civic-assistant-system",
                "civic-assistant-input",
                "civic-assistant-output",
            ],
        },
    ]


def membership_keys(prompt_group: PromptGroup) -> list[str]:
    return list(prompt_group.memberships.order_by("ordering_index").values_list("prompt__key", flat=True))


@pytest.mark.django_db
class TestCreatePromptGroups:
    def test_creates_canonical_groups_and_memberships(self):
        build_prompts()

        prompt_groups = create_prompt_groups(build_group_data())

        assert set(prompt_groups) == {
            "civic-assistant-selection",
            "civic-assistant-answer",
        }
        assert PromptGroup.objects.count() == 2
        assert membership_keys(prompt_groups["civic-assistant-selection"]) == [
            "civic-assistant-system",
            "civic-assistant-input",
        ]
        assert membership_keys(prompt_groups["civic-assistant-answer"]) == [
            "civic-assistant-system",
            "civic-assistant-input",
            "civic-assistant-output",
        ]
        for prompt_group, group_data in zip(prompt_groups.values(), build_group_data(), strict=True):
            assert list(prompt_group.memberships.values_list("ordering_index", flat=True)) == list(
                range(len(group_data["prompts"]))
            )

    def test_is_idempotent_and_preserves_group_and_prompt_primary_keys(self):
        prompts = build_prompts()
        data = build_group_data()

        first_result = create_prompt_groups(data)
        first_group_pks = {key: prompt_group.pk for key, prompt_group in first_result.items()}
        first_prompt_pks = {key: prompt.pk for key, prompt in prompts.items()}

        second_result = create_prompt_groups(data)

        assert PromptGroup.objects.count() == 2
        assert {key: prompt_group.pk for key, prompt_group in second_result.items()} == first_group_pks
        assert {key: prompt.pk for key, prompt in prompts.items()} == first_prompt_pks
        assert membership_keys(second_result["civic-assistant-selection"]) == [
            "civic-assistant-system",
            "civic-assistant-input",
        ]
        assert membership_keys(second_result["civic-assistant-answer"]) == [
            "civic-assistant-system",
            "civic-assistant-input",
            "civic-assistant-output",
        ]

    def test_reorders_existing_memberships(self):
        prompts = build_prompts()
        prompt_group = PromptGroupFactory(key="civic-assistant-selection")
        PromptGroupPromptFactory(prompt_group=prompt_group, prompt=prompts["civic-assistant-input"], ordering_index=0)
        PromptGroupPromptFactory(prompt_group=prompt_group, prompt=prompts["civic-assistant-system"], ordering_index=1)

        result = create_prompt_groups(
            [
                {
                    "key": "civic-assistant-selection",
                    "prompts": ["civic-assistant-system", "civic-assistant-input"],
                }
            ]
        )

        assert result["civic-assistant-selection"].pk == prompt_group.pk
        assert membership_keys(result["civic-assistant-selection"]) == [
            "civic-assistant-system",
            "civic-assistant-input",
        ]

    def test_removes_obsolete_memberships(self):
        prompts = build_prompts()
        prompt_group = PromptGroupFactory(key="civic-assistant-selection")
        PromptGroupPromptFactory(prompt_group=prompt_group, prompt=prompts["civic-assistant-system"], ordering_index=0)
        PromptGroupPromptFactory(prompt_group=prompt_group, prompt=prompts["civic-assistant-input"], ordering_index=1)
        PromptGroupPromptFactory(prompt_group=prompt_group, prompt=prompts["civic-assistant-output"], ordering_index=2)

        create_prompt_groups(
            [
                {
                    "key": "civic-assistant-selection",
                    "prompts": ["civic-assistant-system", "civic-assistant-input"],
                }
            ]
        )

        assert membership_keys(PromptGroup.objects.get(pk=prompt_group.pk)) == [
            "civic-assistant-system",
            "civic-assistant-input",
        ]
        assert not PromptGroupPrompt.objects.filter(
            prompt_group=prompt_group,
            prompt=prompts["civic-assistant-output"],
        ).exists()

    def test_preserves_unrelated_prompts_groups_and_memberships(self):
        build_prompts()
        unrelated_prompt = PromptFactory(key="unrelated-prompt", content="Keep this prompt.")
        unrelated_group = PromptGroupFactory(key="unrelated-group")
        unrelated_membership = PromptGroupPromptFactory(prompt_group=unrelated_group, prompt=unrelated_prompt)

        create_prompt_groups(build_group_data())

        assert Prompt.objects.filter(pk=unrelated_prompt.pk).exists()
        assert PromptGroup.objects.filter(pk=unrelated_group.pk).exists()
        assert PromptGroupPrompt.objects.filter(pk=unrelated_membership.pk).exists()

    def test_validates_duplicate_group_keys_before_synchronizing(self):
        prompts = build_prompts()
        prompt_group = PromptGroupFactory(key="civic-assistant-selection")
        PromptGroupPromptFactory(prompt_group=prompt_group, prompt=prompts["civic-assistant-output"], ordering_index=0)

        with pytest.raises(ValueError, match="Duplicate bootstrap prompt group key"):
            create_prompt_groups(
                [
                    {
                        "key": "civic-assistant-selection",
                        "prompts": ["civic-assistant-system"],
                    },
                    {
                        "key": "civic-assistant-selection",
                        "prompts": ["civic-assistant-input"],
                    },
                ]
            )

        assert membership_keys(PromptGroup.objects.get(pk=prompt_group.pk)) == ["civic-assistant-output"]

    def test_rejects_duplicate_prompt_reference(self):
        build_prompts()

        with pytest.raises(ValueError, match="Duplicate prompt reference"):
            create_prompt_groups([{"key": "group", "prompts": ["civic-assistant-system", "civic-assistant-system"]}])

    def test_rejects_unknown_prompt_reference(self):
        build_prompts()

        with pytest.raises(ValueError, match="does not exist"):
            create_prompt_groups([{"key": "group", "prompts": ["missing-prompt"]}])

    @pytest.mark.parametrize(
        ("data", "message"),
        [
            ({}, "must be a list"),
            (["not a dictionary"], "must be a dictionary"),
            ([{"prompts": ["civic-assistant-system"]}], "exactly"),
            ([{"key": "group", "prompts": [], "extra": True}], "exactly"),
            ([{"key": 42, "prompts": ["civic-assistant-system"]}], "key"),
            ([{"key": "group", "prompts": "not a list"}], "prompts"),
            ([{"key": "group", "prompts": [42]}], "must be a string"),
            ([{"key": "group", "prompts": []}], "at least one prompt"),
        ],
    )
    def test_rejects_invalid_shape(self, data, message):
        with pytest.raises(ValueError, match=message):
            create_prompt_groups(data)  # type: ignore[arg-type]

    def test_rejects_invalid_group_key(self):
        PromptFactory(key="prompt")

        with pytest.raises(ValidationError, match="key"):
            create_prompt_groups([{"key": "invalid key", "prompts": ["prompt"]}])
