import pytest

from .factories import UserProfileFactory


@pytest.fixture
def user_profile(db):
    return UserProfileFactory()
