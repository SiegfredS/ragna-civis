from django.db import models
from django.utils.translation import gettext_lazy as _


class PromptType(models.TextChoices):
    SYSTEM = "system", _("System")
    INPUT_GUARDRAIL = "input_guardrail", _("Input guardrail")
    OUTPUT_GUARDRAIL = "output_guardrail", _("Output guardrail")
