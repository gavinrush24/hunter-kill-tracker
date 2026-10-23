import json
from pathlib import Path

MAPS_FILE = Path(__file__).parent / "maps.json"


def _load_maps():
    """Read the map and animal data from maps.json."""
    with open(MAPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


MAPS = _load_maps()


def get_map_names():
    """Return the list of map names, in the order they appear in maps.json."""
    return list(MAPS.keys())


def get_species_for_map(map_name):
    """Return the list of animals on one map."""
    return MAPS[map_name]


def is_valid_species(map_name, species):
    """Return True if this animal lives on this map."""
    return species in MAPS.get(map_name, [])