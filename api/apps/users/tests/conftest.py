import pytest

from .factories import UserFactory


@pytest.fixture
def user(db):
    return UserFactory()
