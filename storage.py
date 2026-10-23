import json
from pathlib import Path
from species import is_valid_species

DATA_FILE = Path("data/kills.json")


def load_counts():
    """Read the saved kill counts from disk. Returns an empty dict if nothing is saved yet."""
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_counts(counts):
    """Write the kill counts to disk."""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(counts, f, indent=2)


def add_kill(species):
    """Add one kill for a species and return its new total."""
    if not is_valid_species(species):
        raise ValueError(f"Unknown species: {species}")
    counts = load_counts()
    counts[species] = counts.get(species, 0) + 1
    save_counts(counts)
    return counts[species]


if __name__ == "__main__":
    print(add_kill("Moose"))