from pathlib import Path

import customtkinter as ctk
from PIL import Image

BADGES_FOLDER = Path(__file__).parent / "badges"

# Loaded images are kept here so each one is only read from disk once.
_cache = {}


def get_badge_image(species, size):
    """Return this animal's badge as a CTkImage at `size` pixels, or None if there isn't one."""
    key = (species, size)
    if key in _cache:
        return _cache[key]

    file_name = species.lower().replace(" ", "-") + ".png"
    path = BADGES_FOLDER / file_name

    if path.exists():
        picture = Image.open(path)
        image = ctk.CTkImage(light_image=picture, dark_image=picture, size=(size, size))
    else:
        image = None

    _cache[key] = image
    return image