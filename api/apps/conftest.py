from typing import cast

import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient as DRFAPIClient

from apps.profiles.tests.factories import UserProfileFactory
from apps.testing import APIClient
from apps.users.tests.factories import UserFactory


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def user_profile(db):
    return UserProfileFactory()


@pytest.fixture
def http_request():
    return RequestFactory().get("/")


@pytest.fixture
def api_client() -> APIClient:
    return cast(APIClient, DRFAPIClient())
