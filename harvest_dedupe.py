"""Make sure one harvest is logged once, even though the OCR sees it on many frames.

The harvest screen stays up for several seconds, so the detector reads the same
species again and again, and OCR sometimes misses a frame or misreads one. The
rules, counted in frames (the detector checks about twice a second):

1. A kill only counts once the same species has been read on CONFIRM_FRAMES
   frames in a row, so a single misread frame can't log the wrong animal.
2. After a kill, the next one can't count until the harvest screen has been gone
   (no species read) for CLEAR_FRAMES frames in a row. A one-frame OCR dropout in
   the middle of one harvest screen therefore can't count it twice, however long
   the screen stays up, and two separate harvests are both counted however close
   together they are.
"""

CONFIRM_FRAMES = 2
CLEAR_FRAMES = 4  # about 2 seconds at two checks per second


class HarvestDeduper:
    def __init__(self, confirm_frames=CONFIRM_FRAMES, clear_frames=CLEAR_FRAMES):
        self.confirm_frames = confirm_frames
        self.clear_frames = clear_frames
        self._showing = False  # True from a logged kill until its screen has gone
        self._candidate = None  # species being confirmed
        self._streak = 0  # frames in a row the candidate (or "nothing") has been seen

    def update(self, species):
        """Call once per frame with the matched species (or None).

        Returns the species if this frame should log a kill, otherwise None.
        """
        if self._showing:
            # Waiting for the logged harvest screen to really go away.
            if species is None:
                self._streak += 1
                if self._streak >= self.clear_frames:
                    self._showing = False
                    self._candidate, self._streak = None, 0
            else:
                self._streak = 0
            return None

        if species is None:
            self._candidate, self._streak = None, 0
            return None
        if species == self._candidate:
            self._streak += 1
        else:
            self._candidate, self._streak = species, 1
        if self._streak >= self.confirm_frames:
            self._showing = True
            self._streak = 0
            return species
        return None
