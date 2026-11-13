# Plan: Auto-log kills from in-game harvests

## Context
The app (CustomTkinter, `app.py` → `AnimalRow` / `FocusView`, counts in `storage.py`) is fully manual today. Goal: when you harvest an animal in theHunter: COTW, the right animal's kill counter goes up without touching the app. The game has no API, so we build it in two phases (decided):
1. **Global hotkey** — press a key in-game, kill is logged. Builds the "background listener → app" plumbing.
2. **Screen reading (OCR)** — detect the harvest screen, read the species name, and log it automatically through the same plumbing.

Scope: **kills only** (diamonds stay manual for now). Map = whichever reserve is selected in the app.

## Progress
- [x] Step 1: settings + event queue (merged in PR #1)
- [x] Step 2: global F8 hotkey + sidebar switch (merged in PR #2, confirmed working on Windows)
- [ ] Small follow-up: show a message when F8 is pressed with no focus view open
- [ ] Phase 2: species matcher + de-dupe (no game needed), then OCR loop (needs screenshots, resolution, Tesseract)
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
- New `species_matcher.py` (pure function, easy to test): clean OCR text, fuzzy-match it to `maps.get_species_for_map(map)` with stdlib `difflib.get_close_matches`, return the species or `None` below a confidence cutoff. Matching only against the current map's list makes this much more reliable.
- New `harvest_detector.py`: background thread, every ~0.5 s grab only the configured screen region with `mss`, OCR it with `pytesseract` (needs the free Tesseract installer on Windows), pass text to the matcher.
- **De-duplication:** the harvest screen stays up for many frames, so only count on the *transition* from "no match" → "match", plus a cooldown (~10 s). Write this as a small class that takes a clock so it's testable.
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
