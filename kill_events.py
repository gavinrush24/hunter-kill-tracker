"""Messages that background listeners (hotkey, and later OCR) send to the app.

Tkinter is not thread-safe: only the main thread may touch widgets. So a listener
running on its own thread never updates the UI or storage itself. It puts a
KillEvent on a queue.Queue, and the app's main loop picks it up and applies it.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class KillEvent:
    # Where the event came from, e.g. "hotkey" or "ocr". Shown to the user later.
    source: str
    # The animal that was harvested, if the listener knows it (OCR will).
    # None means "whatever animal I'm currently grinding" (the hotkey).
    species: Optional[str] = None


def resolve_target(event, selected_map, focused_species):
    """Work out which (map, species) an event should add a kill to.

    selected_map:    the reserve currently selected in the app.
    focused_species: the animal open in the focus view, or None if it's closed.

    Returns (map_name, species), or None if there's nothing sensible to log.
    """
    if selected_map is None:
        return None
    species = event.species if event.species is not None else focused_species
    if species is None:
        return None
    return (selected_map, species)
