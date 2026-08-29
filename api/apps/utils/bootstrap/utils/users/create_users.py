from typing import Any

from apps.users.models import User

DEFAULT_PASSWORD = "ragna-civis"


def create_users(data: list[dict[str, Any]]) -> dict[str, User]:
    """Create bootstrap users keyed by username."""
    users: dict[str, User] = {}

    for user_data in data:
        username, user = create_user(data=user_data)
        users[username] = user

    return users


def create_user(data: dict[str, Any]) -> tuple[str, User]:
    password = data.get("password", DEFAULT_PASSWORD)

    user, _ = User.objects.update_or_create(
        username=data["username"],
        defaults={
            "email": data["email"],
            "first_name": data.get("first_name", ""),
            "middle_name": data.get("middle_name", ""),
            "last_name": data.get("last_name", ""),
            "is_staff": data.get("is_staff", False),
            "is_superuser": data.get("is_superuser", False),
        },
    )

    user.set_password(password)
    user.save(update_fields=["password"])

    return (user.username, user)
