import logging
import os
from collections.abc import Callable
from typing import TypeVar

from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)
T = TypeVar("T")


def get_required_env(name: str) -> str:
    """Return a non-blank environment variable or fail during configuration."""
    value = os.environ.get(name, "").strip()

    if not value:
        raise ImproperlyConfigured(f"The {name} environment variable is required.")

    return value


def get_env_with_default(getter: Callable[..., T], name: str, default: T) -> T:
    """Read a typed environment variable, warning and using a default if absent."""
    if not os.environ.get(name, "").strip():
        logger.warning("The %s environment variable is not configured; using its default.", name)
        return default

    return getter(name, default=default)
