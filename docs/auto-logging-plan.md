# Plan: Auto-log kills from in-game harvests

## Context
The app (CustomTkinter, `app.py` → `AnimalRow` / `FocusView`, counts in `storage.py`) is fully manual today. Goal: when you harvest an animal in theHunter: COTW, the right animal's kill counter goes up without touching the app. The game has no API, so we build it in two phases (decided):
1. **Global hotkey** — press a key in-game, kill is logged. Builds the "background listener → app" plumbing.
2. **Screen reading (OCR)** — detect the harvest screen, read the species name, and log it automatically through the same plumbing.

Scope: **kills only** (diamonds stay manual for now). Map = whichever reserve is selected in the app.

## Progress
- [x] Step 1: settings + event queue (merged in PR #1)
- [x] Step 2: global F8 hotkey + sidebar switch (merged in PR #2, confirmed working on Windows)
- [x] Small follow-up: show a message when F8 is pressed with no focus view open
- [x] Toast with Undo after every auto-logged kill
- [x] Phase 2: `species_matcher.py` and `harvest_dedupe.py`, with tests (no game needed)
- [x] Fixed matcher/de-dupe issues found in code review (Goose→Moose, Red/Roe Deer ties, dropped and double-counted kills)
- [ ] **Next:** Phase 2 OCR loop (`harvest_detector.py`). Blocked on: harvest-screen screenshots in `tests/fixtures/`, your screen resolution, and Tesseract installed
- [x] Plan saved in the repo at `docs/auto-logging-plan.md`

## Core design (shared by both phases)
- Listeners run on a **background thread** and never touch the UI or storage directly — Tkinter isn't thread-safe. They put events like `("kill", map_name, species)` onto a `queue.Queue`.
- `app.py` polls the queue every ~100 ms with `self.after(...)`, calls the existing `storage.add_kill(map, species)`, then refreshes the visible `AnimalRow` (`self.rows[species].reload()`) or the open `FocusView`.
- Show a small toast in the app: "Logged Whitetail Deer (auto) — Undo" (Undo calls `storage.remove_kill`). Important because detection can be wrong.
- A settings file (`data/settings.json`, next to `tracker.json`, via `paths.app_folder()`) holds the hotkey, auto-detect on/off, and OCR region.

## Phase 1 — Global hotkey
- New `hotkey_listener.py`: uses `pynput` (no admin rights needed on Windows) to listen for a configurable key (default e.g. `F8`) even while the game is focused.
- Target animal = the animal open in `FocusView` (fits your one-animal grind workflow). If no focus view is open, ignore the key and show a hint.
- Add an on/off switch in the sidebar ("Auto-logging").
- Add `pynput` to `requirements.txt`; check the PyInstaller build still works.

## Phase 2 — Harvest screen OCR
- **Step 0 (research, do first):** take screenshots of the harvest/trophy screen at your resolution for several species. Save a few in `tests/fixtures/`. This tells us exactly where the species name appears. Run the game in **borderless windowed** — fullscreen exclusive can block screen capture.
- `species_matcher.py` (pure function, easy to test): clean OCR text (look-alike digits fixed), check for an exact name first, then fuzzy-match each line, each pair of neighbouring lines (wrapped names) and the whole text against `maps.get_species_for_map(map)` with stdlib `difflib`. Returns `None` when unsure: below the cutoff, short names (≤ 6 letters, e.g. Moose/Goose) need ≥ 0.9, and a runner-up within 0.05 counts as ambiguous (Red/Roe Deer). Logging the wrong animal is worse than logging nothing.
- New `harvest_detector.py`: background thread, every ~0.5 s grab only the configured screen region with `mss`, OCR it with `pytesseract` (needs the free Tesseract installer on Windows), pass text to the matcher.
- **De-duplication** (`harvest_dedupe.py`, frame-based, no clock): a kill counts only after the same species is read on 2 frames in a row, and the next kill can't count until no species has been read for 4 frames in a row (~2 s). This replaced a 10 s cooldown that dropped real back-to-back kills and double-counted long harvest screens with a one-frame OCR dropout.
- Region stored in settings as screen percentages so it survives resolution changes; later add a "calibrate" button.
- Detection hands events to the same queue as Phase 1 — no app changes beyond a second switch.

## Files
- Modify: `app.py` (queue polling, toast, switches), `focus_view.py` (refresh after external change, if no method exists), `requirements.txt`, `README.md`.
- New: `hotkey_listener.py`, `settings.py`, `species_matcher.py`, `harvest_detector.py`, tests for each pure piece.
- Reuse: `storage.add_kill/remove_kill`, `maps.get_species_for_map`, `paths.app_folder`, `AnimalRow.reload`.

## Engineering habits
- Work on a feature branch; one commit per step (settings → queue plumbing → hotkey → matcher → dedupe → OCR loop).
- Unit tests (pytest, matching `tests/test_storage.py` style): `test_species_matcher.py` (exact, typo'd, wrong-map, garbage text), `test_dedupe.py` (fake clock), `test_settings.py` (defaults when file missing).
- Keep OCR/hotkey code thin; put logic in pure functions so it's testable without the game.

## Verification
- `pytest` passes.
- Phase 1: open a focus view, alt-tab to another window, press the hotkey → counter increments, toast appears, Undo works.
- Phase 2: run the detector against fixture screenshots (offline test) → correct species, one event each. Then in-game: harvest an animal → exactly one kill logged for the right species.
- Rebuild the exe with PyInstaller and repeat a quick hotkey test.
