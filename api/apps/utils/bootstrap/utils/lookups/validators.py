from django.db.models import TextChoices


def validate_choice(
    value: str,
    *,
    choices: type[TextChoices],
    field_name: str,
) -> str:
    if value not in choices.values:
        raise ValueError(f"Invalid {field_name} {value!r}. Expected one of {choices.values}.")

    return value
