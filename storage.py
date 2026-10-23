import json
from pathlib import Path

DATA_FILE = Path("data/tracker.json")


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
    }


def _change_count(map_name, species, field, amount):
    """Add `amount` (can be negative) to a field, never dropping below 0. Returns the new value."""
    data = load_data()
    map_data = data.setdefault(map_name, {})
    entry = map_data.setdefault(species, {"kills": 0, "diamonds": 0})
    entry[field] = max(0, entry.get(field, 0) + amount)
    save_data(data)
    return entry[field]


def add_kill(map_name, species):
    return _change_count(map_name, species, "kills", 1)


def remove_kill(map_name, species):
    return _change_count(map_name, species, "kills", -1)


def add_diamond(map_name, species):
    return _change_count(map_name, species, "diamonds", 1)


def remove_diamond(map_name, species):
    return _change_count(map_name, species, "diamonds", -1)


if __name__ == "__main__":
    print(add_kill("Medved Taiga", "Moose"))