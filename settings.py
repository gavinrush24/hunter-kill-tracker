import json

from paths import app_folder

SETTINGS_FILE = app_folder() / "data" / "settings.json"

# Used for any setting that isn't in the file yet (or when there is no file at all).
DEFAULTS = {
    "hotkey": "f8",
    "auto_logging": False,
}


def load_settings():
    """Read settings from disk, filling in a default for anything missing.

    A missing or broken file is not an error: we just fall back to the defaults,
    so a bad settings file can never stop the app from opening.
    """
    settings = dict(DEFAULTS)
    if not SETTINGS_FILE.exists():
        return settings
    try:
        with open(SETTINGS_FILE, "r") as f:
            saved = json.load(f)
    except (json.JSONDecodeError, OSError):
        return settings
    if isinstance(saved, dict):
        # Only keep keys we know about, so old or misspelled keys are ignored.
        for key in DEFAULTS:
            if key in saved:
                settings[key] = saved[key]
    return settings


def save_settings(settings):
    """Write settings to disk."""
    SETTINGS_FILE.parent.mkdir(exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
