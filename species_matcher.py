"""Turn messy OCR text from the harvest screen into one of the map's species names.

This is a pure function on purpose: it can be tested without the game, the
screen, or Tesseract. Only the current map's animals are considered, which makes
matching far more reliable than guessing from every animal in the game.
"""

import difflib
import re

# Common OCR mix-ups: digits read in place of the letters they look like.
_LOOKALIKES = str.maketrans({"0": "o", "1": "l", "5": "s", "8": "b", "|": "l"})


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


def match_species(text, species_list, cutoff=0.8):
    """Return the species from species_list that the text names, or None.

    cutoff: how similar (0 to 1) a line must be to a name to count as a fuzzy match.
    """
    if not text:
        return None
    cleaned = clean_text(text)
    if not cleaned:
        return None
    by_clean_name = {clean_text(species): species for species in species_list}

    # 1. The exact name appears somewhere in the text. Try longer names first, so
    #    "Whitetail Deer" isn't beaten by a shorter name that happens to be inside it.
    padded = f" {cleaned.replace(chr(10), ' ')} "
    for name in sorted(by_clean_name, key=len, reverse=True):
        if f" {name} " in padded:
            return by_clean_name[name]

    # 2. No exact hit: find the closest name to any single line, or to the whole text.
    candidates = cleaned.split("\n") + [cleaned.replace("\n", " ")]
    best_name, best_score = None, cutoff
    for candidate in candidates:
        for name in difflib.get_close_matches(candidate, by_clean_name, n=1, cutoff=cutoff):
            score = difflib.SequenceMatcher(None, candidate, name).ratio()
            if score >= best_score:
                best_name, best_score = name, score
    return by_clean_name[best_name] if best_name is not None else None
