# Hunter Kill Tracker

A desktop app for tracking kills and diamond animals in **theHunter: Call of the Wild**, built with Python and CustomTkinter.

<!-- Add a screenshot once you have one: save it as docs/screenshot.png and uncomment the next line -->
<!-- ![Hunter Kill Tracker screenshot](docs/screenshot.png) -->

## Why this exists

Grinding for diamond animals means hunting the same species over and over. This app keeps a running count of kills and diamonds for every animal on every reserve, and works out your diamond rate (kills per diamond) so you can see how your grind is going.

## Features

- **Per-reserve tracking.** Every reserve has its own list of animals and its own counters, matching how the game keeps populations separate for each map.
- **Kill and diamond counters** for each animal, with `+` and `-` buttons.
- **Diamond rate** shown for every animal as kills per diamond, to two decimal places (for example, 300 kills and 6 diamonds shows `1 every 50.00`).
- **Focus view.** Click an animal's badge to open a full-window view with a large badge and large counters, built for grinding one animal at a time.
- **Pinning.** Pin the animals you're working on and they move to the top of their reserve's list.
- **Automatic saving.** Everything is saved to a local file as you go and is there when you reopen the app.
- **Badge images** for each animal, with a placeholder shown for any animal that doesn't have one.

## Getting started

You'll need **Python 3.9 or newer**.

```bash
git clone https://github.com/YOUR-USERNAME/hunter-kill-tracker.git
cd hunter-kill-tracker
```

Create and activate a virtual environment (recommended):

```bash
# Windows (PowerShell)
py -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies and run the app:

```bash
# Windows
py -m pip install -r requirements.txt
py app.py

# macOS / Linux
python3 -m pip install -r requirements.txt
python3 app.py
```

## Adding badge images

The badge artwork belongs to the game's developer, so it is **not included in this repository**. The app works without it and shows a letter placeholder for each animal, but you can add your own images to get the full look.

1. Create a folder named `badges` in the project root (next to `app.py`).
2. Add one PNG per animal. Transparent backgrounds look best, and 200x200 pixels or larger works well.
3. Name each file after the animal, in lowercase with hyphens, matching the spelling in `maps.json`:

| Animal | File name |
|---|---|
| Whitetail Deer | `whitetail-deer.png` |
| Roosevelt Elk | `roosevelt-elk.png` |
| White-tailed Jackrabbit | `white-tailed-jackrabbit.png` |

The `badges` folder is listed in `.gitignore`, so your images won't be uploaded if you fork or contribute.

## Where your data is saved

Your counts and pins are stored in `data/tracker.json`, created automatically the first time you log something. It's a plain JSON file, so you can back it up by copying it. The `data` folder is also in `.gitignore`.

## Adding or fixing animals and reserves

All reserve and animal data lives in [`maps.json`](maps.json). It maps each reserve name to the list of animals found there, and the app builds its sidebar and animal lists from it, so adding a reserve or fixing a spelling needs no code changes:

```json
{
  "Layton Lake District": [
    "Black Bear",
    "Coyote",
    "Moose"
  ]
}
```

Animal names must match your badge file names (see above). If you notice a missing animal or a wrong name, a fix to `maps.json` is a great first contribution.

**Current coverage:** Hirschfelden Hunting Reserve and Layton Lake District. More reserves are being added.

## Project structure

```
hunter-kill-tracker/
├── app.py            # main window: reserve sidebar and animal list
├── animal_row.py     # one row in the list (badge, name, pin, counters, rate)
├── focus_view.py     # the full-window single-animal view
├── badges.py         # loads badge images, with caching and a fallback
├── maps.py           # loads maps.json and answers "which animals are on this map?"
├── maps.json         # reserve and animal data
├── stats.py          # diamond rate calculation and formatting
├── storage.py        # saving and loading counts and pins (JSON)
├── theme.py          # shared colors
└── requirements.txt
```

The code is split so that each file has one job. The data and logic (`storage.py`, `maps.py`, `stats.py`) don't know anything about the window, and the window files only talk to them through a handful of functions.

## Built with

- [Python](https://www.python.org/)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the interface
- [Pillow](https://python-pillow.org/) for loading badge images

## Roadmap

- [ ] Add the remaining reserves
- [ ] Keyboard shortcuts (for example, leaving the focus view with Escape)
- [ ] Session totals alongside all-time totals
- [ ] Tests for the storage and rate logic
- [ ] Packaged Windows `.exe` so Python isn't required

## Disclaimer

This is an unofficial fan project and is not affiliated with or endorsed by Expansive Worlds, Avalanche Studios, or the makers of theHunter: Call of the Wild. All game names and artwork belong to their respective owners. The app doesn't read, modify, or interact with the game or its files in any way. It only keeps its own counts.