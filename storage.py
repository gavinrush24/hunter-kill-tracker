import json
from pathlib import Path

from maps import is_valid_species

DATA_FILE = Path("data/tracker.json")

# Kills and diamonds logged since the app was opened, keyed by (map, species).
# This lives in memory only, so it starts empty every time the app runs.
_session = {}


def load_data():
    """Read all saved data from disk. Returns an empty dict if nothing is saved yet."""
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    """Write all data to disk."""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_entry(map_name, species):
    """Return {'kills': n, 'diamonds': n} for one animal on one map (zeros if never logged)."""
    data = load_data()
    entry = data.get(map_name, {}).get(species, {})
    return {
        "kills": entry.get("kills", 0),
        "diamonds": entry.get("diamonds", 0),
        "pinned": entry.get("pinned", False),
    }


def get_session(map_name, species):
    """Return {'kills': n, 'diamonds': n} logged since the app was opened."""
    entry = _session.get((map_name, species), {})
    return {
        "kills": entry.get("kills", 0),
        "diamonds": entry.get("diamonds", 0),
    }


def _record_session_change(map_name, species, field, change):
    """Add the change that was actually made to this animal's session count (never below 0)."""
    entry = _session.setdefault((map_name, species), {"kills": 0, "diamonds": 0})
    entry[field] = max(0, entry[field] + change)


def _change_count(map_name, species, field, amount):
    """Add `amount` (can be negative) to a field, never dropping below 0. Returns the new value."""
    if not is_valid_species(map_name, species):
        raise ValueError(f"{species} is not a known animal on {map_name}")
    data = load_data()
    map_data = data.setdefault(map_name, {})
    entry = map_data.setdefault(species, {"kills": 0, "diamonds": 0})
    old_value = entry.get(field, 0)
    entry[field] = max(0, old_value + amount)
    save_data(data)
    # Use the real change (not `amount`) so removing from a count that is already 0 does nothing.
    _record_session_change(map_name, species, field, entry[field] - old_value)
    return entry[field]


def add_kill(map_name, species):
    return _change_count(map_name, species, "kills", 1)


def remove_kill(map_name, species):
    return _change_count(map_name, species, "kills", -1)


def add_diamond(map_name, species):
    return _change_count(map_name, species, "diamonds", 1)


def remove_diamond(map_name, species):
    return _change_count(map_name, species, "diamonds", -1)


def toggle_pin(map_name, species):
    """Flip an animal's pinned state. Returns the new state (True if now pinned)."""
    if not is_valid_species(map_name, species):
        raise ValueError(f"{species} is not a known animal on {map_name}")
    data = load_data()
    map_data = data.setdefault(map_name, {})
    entry = map_data.setdefault(species, {"kills": 0, "diamonds": 0})
    entry["pinned"] = not entry.get("pinned", False)
    save_data(data)
    return entry["pinned"]


def reset_animal(map_name, species):
    """Set an animal's kills and diamonds back to zero, including its session. Pinned state is kept."""
    if not is_valid_species(map_name, species):
        raise ValueError(f"{species} is not a known animal on {map_name}")
    data = load_data()
    map_data = data.setdefault(map_name, {})
    entry = map_data.setdefault(species, {"kills": 0, "diamonds": 0})
    entry["kills"] = 0
    entry["diamonds"] = 0
    save_data(data)
    _session.pop((map_name, species), None)


if __name__ == "__main__":
    print(add_kill("Layton Lake District", "Whitetail Deer"))
    print(add_diamond("Layton Lake District", "Whitetail Deer"))
    print(get_entry("Layton Lake District", "Whitetail Deer"))
    print(get_entry("Hirschfelden Hunting Reserve", "Red Deer"))