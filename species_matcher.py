"""Turn messy OCR text from the harvest screen into one of the map's species names.

This is a pure function on purpose: it can be tested without the game, the
screen, or Tesseract. Only the current map's animals are considered, which makes
matching far more reliable than guessing from every animal in the game.

Logging the wrong animal is worse than logging nothing (the user can always press
F8 instead), so when in doubt the matcher returns None.
"""

import difflib
import re

# Common OCR mix-ups: digits read in place of the letters they look like.
_LOOKALIKES = str.maketrans({"0": "o", "1": "l", "5": "s", "8": "b", "|": "l"})

# Names this short need a near-exact match: one wrong letter in "Moose" gives
# "Goose" or "Mouse", which are real words, not OCR noise.
SHORT_NAME_LENGTH = 6
SHORT_NAME_CUTOFF = 0.9

# If the runner-up animal scores within this much of the best one, the text is
# ambiguous (e.g. "Rod Deer" is equally close to Red Deer and Roe Deer).
AMBIGUITY_MARGIN = 0.05


def clean_text(text):
    """Lowercase the text, fix look-alike digits, and keep only letters, spaces and hyphens.

    Hyphens become spaces, so "White-tailed" and "White tailed" compare equal.
    Line breaks are kept so each line can be matched on its own.
    """
    lines = []
    for line in text.lower().translate(_LOOKALIKES).splitlines():
        line = re.sub(r"[^a-z\- ]", " ", line).replace("-", " ")
        line = " ".join(line.split())
        if line:
            lines.append(line)
    return "\n".join(lines)


def _candidates(cleaned):
    """The pieces of text worth comparing to names: each line, each pair of
    neighbouring lines (for names that wrap), and the whole text."""
    lines = cleaned.split("\n")
    pairs = [f"{a} {b}" for a, b in zip(lines, lines[1:])]
    return lines + pairs + [" ".join(lines)]


def match_species(text, species_list, cutoff=0.8):
    """Return the species from species_list that the text names, or None.

    cutoff: how similar (0 to 1) the text must be to a name to count as a fuzzy
    match. Short names always need at least SHORT_NAME_CUTOFF.
    """
    if not text:
        return None
    cleaned = clean_text(text)
    if not cleaned:
        return None
    by_clean_name = {clean_text(species): species for species in species_list}

    # 1. The exact name appears somewhere in the text, as whole words. Try longer names
    #    first, so "Whitetail Deer" isn't beaten by a shorter name that happens to be inside it.
    padded = f" {cleaned.replace(chr(10), ' ')} "
    for name in sorted(by_clean_name, key=len, reverse=True):
        if f" {name} " in padded:
            return by_clean_name[name]

    # 2. No exact hit: score every name against its closest piece of text.
    candidates = _candidates(cleaned)
    scores = {
        name: max(difflib.SequenceMatcher(None, piece, name).ratio() for piece in candidates)
        for name in by_clean_name
    }
    ranked = sorted(scores, key=scores.get, reverse=True)
    best = ranked[0]
    needed = SHORT_NAME_CUTOFF if len(best) <= SHORT_NAME_LENGTH else cutoff
    if scores[best] < max(cutoff, needed):
        return None
    if len(ranked) > 1 and scores[best] - scores[ranked[1]] < AMBIGUITY_MARGIN:
        return None
    return by_clean_name[best]
