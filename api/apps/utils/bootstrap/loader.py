import json
from pathlib import Path
from typing import Any

from django.conf import settings

BOOTSTRAP_DATA_DIR: Path = settings.BASE_DIR / "apps" / "utils" / "bootstrap" / "data"
DEFAULT_DATA_DIR = BOOTSTRAP_DATA_DIR / "bootstrap_data.json"
DEFAULT_DEV_DATA_DIR = BOOTSTRAP_DATA_DIR / "bootstrap_dev_data.json"


def load_bootstrap_data(*, include_dev: bool = False) -> dict[str, Any]:
    """Load the base bootstrap data and optional development-only data."""
    data = _load_json(DEFAULT_DATA_DIR)

    if include_dev:
        dev_data = _load_json(BOOTSTRAP_DATA_DIR / "bootstrap_dev_data.json")

        for key, values in dev_data.items():
            data.setdefault(key, [])
            data[key].extend(values)

    return data


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)
