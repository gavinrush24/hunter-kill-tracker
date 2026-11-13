import json

import pytest

import settings


@pytest.fixture(autouse=True)
def settings_file(tmp_path, monkeypatch):
    # Point settings at a temporary file so the real data/settings.json is never touched.
    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings, "SETTINGS_FILE", path)
    return path


def test_defaults_when_no_file_exists():
    assert settings.load_settings() == settings.DEFAULTS


def test_saved_settings_are_loaded_back():
    settings.save_settings({"hotkey": "f9", "auto_logging": True})
    assert settings.load_settings() == {"hotkey": "f9", "auto_logging": True}


def test_missing_keys_fall_back_to_defaults(settings_file):
    settings_file.write_text(json.dumps({"hotkey": "f9"}))
    loaded = settings.load_settings()
    assert loaded["hotkey"] == "f9"
    assert loaded["auto_logging"] == settings.DEFAULTS["auto_logging"]


def test_unknown_keys_are_ignored(settings_file):
    settings_file.write_text(json.dumps({"hotkey": "f9", "colour": "blue"}))
    assert "colour" not in settings.load_settings()


def test_broken_file_falls_back_to_defaults(settings_file):
    settings_file.write_text("{ this is not json")
    assert settings.load_settings() == settings.DEFAULTS


def test_loading_does_not_change_the_defaults():
    # load_settings must copy DEFAULTS, not hand out the shared dict.
    loaded = settings.load_settings()
    loaded["hotkey"] = "changed"
    assert settings.DEFAULTS["hotkey"] == "f8"
