import pytest

from apps.profiles.models import UserProfile


@pytest.mark.django_db
class TestUserProfileModel:
    def test_user_profile_factory_creates_a_profile(self, user_profile):
        assert isinstance(user_profile, UserProfile)
        assert user_profile.pk is not None
        profile = UserProfile.objects.get(pk=user_profile.pk)
        assert profile.user.id == user_profile.user.id
        assert user_profile.created is not None
        assert user_profile.modified is not None

    def test_str(self, user_profile):
        assert str(user_profile) == str(user_profile.user)

    def test_deleting_user_deletes_profile(self, user_profile):
        user = user_profile.user
        profile_id = user_profile.pk

        user.delete()

        assert not UserProfile.objects.filter(pk=profile_id).exists()
