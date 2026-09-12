import json
from pathlib import Path
from typing import Any

from django.conf import settings

BOOTSTRAP_DATA_DIR: Path = settings.BASE_DIR / "apps" / "utils" / "bootstrap" / "data"
BASE_BOOTSTRAP_FILES = (
    "users.json",
    "civic_assistant.json",
    "organizations.json",
    "governance.json",
    "projects.json",
)
DEFAULT_DEV_DATA_DIR = BOOTSTRAP_DATA_DIR / "bootstrap_dev_data.json"


def load_bootstrap_data(*, include_dev: bool = False) -> dict[str, Any]:
    """Load the base bootstrap data and optional development-only data."""
    data: dict[str, Any] = {}

    for filename in BASE_BOOTSTRAP_FILES:
        base_data = _load_json(BOOTSTRAP_DATA_DIR / filename)

        for key, values in base_data.items():
            if key in data:
                raise ValueError(f"Duplicate bootstrap data section '{key}' in base files")

            data[key] = values

    if include_dev:
        dev_data = _load_json(DEFAULT_DEV_DATA_DIR)

        for key, values in dev_data.items():
            data.setdefault(key, [])
            data[key].extend(values)

    return data


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)
