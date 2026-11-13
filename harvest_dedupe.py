"""Make sure one harvest is logged once, even though the OCR sees it on many frames.

The harvest screen stays up for several seconds, so the detector reads the same
species again and again. A kill only counts when the screen *changes* to showing
a species, and never twice within the cooldown.
"""

import time


class HarvestDeduper:
    def __init__(self, cooldown=10.0, clock=time.monotonic):
        """cooldown: seconds that must pass after a logged kill before the next one.
        clock: returns the current time in seconds (tests pass a fake one).
        """
        self.cooldown = cooldown
        self._clock = clock
        self._last_seen = None
        self._last_fired_at = None

    def update(self, species):
        """Call once per frame with the matched species (or None).

        Returns the species if this frame should log a kill, otherwise None.
        """
        previous = self._last_seen
        self._last_seen = species
        if species is None or species == previous:
            return None
        now = self._clock()
        if self._last_fired_at is not None and now - self._last_fired_at < self.cooldown:
            return None
        self._last_fired_at = now
        return species
