from apps.civic_assistant.models import Prompt


def get_prompt(*, key: str) -> Prompt:
    try:
        return Prompt.objects.get(key=key)
    except Prompt.DoesNotExist as error:
        raise ValueError(f"Bootstrap prompt with key {key!r} does not exist.") from error
    except Prompt.MultipleObjectsReturned as error:
        raise ValueError(f"Bootstrap prompt with key {key!r} is ambiguous.") from error
