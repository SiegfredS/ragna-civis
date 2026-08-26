from django.db import models


def max_choice_value_length(choices: type[models.Choices]) -> int:
    """Return the maximum stored value length for Django model choices."""
    return max(len(str(choice.value)) for choice in choices)
