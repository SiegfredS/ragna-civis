from apps.profiles.models import UserProfile


def get_user_profile(*, username: str) -> UserProfile:
    try:
        return UserProfile.objects.get(user__username=username)
    except UserProfile.DoesNotExist as error:
        raise ValueError(f"Bootstrap user profile for username {username!r} does not exist.") from error
