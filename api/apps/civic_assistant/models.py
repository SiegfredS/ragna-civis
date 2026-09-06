from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.civic_assistant.choices import PromptType
from apps.utils.models import TimeStampedModel
from apps.utils.utils import max_choice_value_length


class Prompt(TimeStampedModel):
    key = models.SlugField(
        verbose_name=_("key"),
        max_length=124,
        unique=True,
    )
    prompt_type = models.CharField(
        verbose_name=_("prompt type"),
        max_length=max_choice_value_length(PromptType),
        choices=PromptType.choices,
    )
    content = models.TextField()

    def __str__(self) -> str:
        return self.key

    def clean(self) -> None:
        super().clean()

        if not isinstance(self.content, str) or not self.content.strip():
            raise ValidationError({"content": "Prompt content cannot be blank"})

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("Prompt")
        verbose_name_plural = _("Prompts")
        ordering = ["-created"]


class PromptGroup(TimeStampedModel):
    key = models.SlugField(
        verbose_name=_("key"),
        max_length=124,
        unique=True,
    )

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("Prompt group")
        verbose_name_plural = _("Prompt groups")
        ordering = ["-created"]

    def __str__(self) -> str:
        return self.key


class PromptGroupPrompt(TimeStampedModel):
    prompt_group = models.ForeignKey(
        PromptGroup,
        verbose_name=_("prompt group"),
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    prompt = models.ForeignKey(
        Prompt,
        verbose_name=_("prompt"),
        on_delete=models.CASCADE,
        related_name="group_memberships",
    )
    ordering_index = models.PositiveIntegerField()

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("Prompt Group Prompt")
        verbose_name_plural = _("Prompt Group Prompts")
        ordering = ["prompt_group_id", "ordering_index"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "prompt_group",
                    "prompt",
                ],
                name="unique_prompt_group_prompt",
            ),
            models.UniqueConstraint(
                fields=[
                    "prompt_group",
                    "ordering_index",
                ],
                name="unique_prompt_group_ordering_index",
            ),
        ]
