import json

import pytest

from apps.utils.bootstrap import loader


def test_load_bootstrap_data_returns_all_base_sections_without_dev_user():
    data = loader.load_bootstrap_data()

    assert set(data) == {
        "users",
        "prompts",
        "prompt_groups",
        "organizations",
        "organization_memberships",
        "governance_bodies",
        "governance_positions",
        "governance_position_assignments",
        "projects",
    }
    assert not any(user["username"] == "admin" for user in data["users"])


def test_load_bootstrap_data_dev_overlay_appends_dev_users():
    base_data = loader.load_bootstrap_data()
    dev_data = loader.load_bootstrap_data(include_dev=True)

    assert dev_data.keys() == base_data.keys()
    assert dev_data["users"][: len(base_data["users"])] == base_data["users"]
    assert any(user["username"] == "admin" for user in dev_data["users"])


def test_load_bootstrap_data_rejects_duplicate_base_sections(tmp_path, monkeypatch):
    (tmp_path / "first.json").write_text(json.dumps({"users": []}), encoding="utf-8")
    (tmp_path / "second.json").write_text(json.dumps({"users": []}), encoding="utf-8")
    monkeypatch.setattr(loader, "BOOTSTRAP_DATA_DIR", tmp_path)
    monkeypatch.setattr(loader, "BASE_BOOTSTRAP_FILES", ("first.json", "second.json"))

    with pytest.raises(ValueError, match="Duplicate bootstrap data section 'users'"):
        loader.load_bootstrap_data()
