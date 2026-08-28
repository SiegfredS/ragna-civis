import pytest

from .factories import ProjectFactory


@pytest.fixture
def project(db):
    return ProjectFactory()
