import customtkinter as ctk
from PIL import Image
from paths import app_folder

BADGES_FOLDER = app_folder() / "badges"

# Loaded images are kept here so each one is only read from disk once.
_cache = {}


def get_badge_image(species, size):
    """Return this animal's badge as a CTkImage at `size` pixels, or None if there isn't one.

    A badge file that can't be opened (damaged, or not really a PNG) also gives None,
    so the animal just shows its letter placeholder instead of breaking the list.
    """
    key = (species, size)
    if key in _cache:
        return _cache[key]

    file_name = species.lower().replace(" ", "-") + ".png"
    path = BADGES_FOLDER / file_name

    image = None
    if path.exists():
        try:
            # copy() reads the whole picture now, so the file isn't held open afterwards.
            with Image.open(path) as opened:
                picture = opened.copy()
            image = ctk.CTkImage(light_image=picture, dark_image=picture, size=(size, size))
        except (OSError, ValueError):  # PIL's UnidentifiedImageError is an OSError
            image = None

    _cache[key] = image
    return image


class BadgeLabel(ctk.CTkLabel):
    """A CTkLabel for a cached badge image that lets go of the image when destroyed.

    CTkLabel registers itself with its CTkImage but (in customtkinter 6.0) never
    unregisters. Since badge images are cached for the whole session, every destroyed
    row would otherwise stay in memory, and switching reserves would slowly leak them.
    """

    def destroy(self):
        image = getattr(self, "_image", None)
        if isinstance(image, ctk.CTkImage):
            try:
                image.remove_configure_callback(self._update_image)
            except ValueError:
                pass  # already removed (e.g. a future customtkinter does it itself)
        super().destroy()
