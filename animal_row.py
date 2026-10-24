import customtkinter as ctk

import storage
from badges import get_badge_image
from stats import diamond_rate_text
from theme import (
    ORANGE,
    ORANGE_HOVER,
    MUTED_TEXT,
    SEPARATOR,
    NEUTRAL_BUTTON,
    NEUTRAL_BUTTON_HOVER,
    BUTTON_TEXT,
)

ROW_HEIGHT = 96
BADGE_SIZE = 64


class AnimalRow(ctk.CTkFrame):
    """One animal's row: badge, name, pin, kills counter, diamonds counter, diamond rate."""

    def __init__(self, parent, map_name, species, on_open, on_pin_change):
        super().__init__(parent, height=ROW_HEIGHT, fg_color="transparent")
        self.map_name = map_name
        self.species = species
        self.on_open = on_open  # called with the species name when the badge is clicked
        self.on_pin_change = on_pin_change  # called (no arguments) after the pin is toggled

        entry = storage.get_entry(map_name, species)
        self.kills = entry["kills"]
        self.diamonds = entry["diamonds"]
        self.pinned = entry["pinned"]

        # Keep the row at a fixed height instead of shrinking to fit its contents.
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)  # the name column stretches
        self.grid_rowconfigure(0, weight=1)

        self._build_badge()
        self._build_name()
        self.kills_label = self._build_counter(
            column=2,
            title="Kills",
            on_minus=lambda: self._change_kills(storage.remove_kill),
            on_plus=lambda: self._change_kills(storage.add_kill),
        )
        self.diamonds_label = self._build_counter(
            column=3,
            title="Diamonds",
            on_minus=lambda: self._change_diamonds(storage.remove_diamond),
            on_plus=lambda: self._change_diamonds(storage.add_diamond),
        )
        self.rate_label = self._build_rate()

        # The line under the row.
        separator = ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=SEPARATOR)
        separator.grid(row=1, column=0, columnspan=5, sticky="ew")

        self._refresh()

    def _build_badge(self):
        badge = ctk.CTkFrame(
            self,
            width=BADGE_SIZE,
            height=BADGE_SIZE,
            corner_radius=12,
            border_width=2,
            border_color=ORANGE,
            fg_color=("gray85", "gray20"),
        )
        badge.grid(row=0, column=0, padx=(12, 16))
        badge.grid_propagate(False)
        badge.grid_rowconfigure(0, weight=1)
        badge.grid_columnconfigure(0, weight=1)

        image = get_badge_image(self.species, BADGE_SIZE)
        if image is not None:
            # A real badge: drop the placeholder's orange border and background.
            badge.configure(border_width=0, fg_color="transparent")
            label = ctk.CTkLabel(badge, text="", image=image)
        else:
            label = ctk.CTkLabel(
                badge, text=self.species[0], font=ctk.CTkFont(size=26, weight="bold")
            )
        label.grid(row=0, column=0)

        # Clicking the badge (or the image/letter on top of it) opens the focus view.
        for widget in (badge, label):
            widget.bind("<Button-1>", lambda event: self.on_open(self.species))
            widget.configure(cursor="hand2")

    def _build_name(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=1, sticky="w", padx=(0, 12))

        name = ctk.CTkLabel(
            frame,
            text=self.species,
            anchor="w",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        name.grid(row=0, column=0)

        # The star's look (filled or empty) is set in _refresh.
        self.pin_button = ctk.CTkButton(
            frame,
            text="",
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=NEUTRAL_BUTTON,
            font=ctk.CTkFont(family="Segoe UI Symbol", size=20),
            command=self._toggle_pin,
        )
        self.pin_button.grid(row=0, column=1, padx=(8, 0))

    def _build_counter(self, column, title, on_minus, on_plus):
        """Build a titled counter with - and + buttons. Returns the label showing the number."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=column, padx=14)

        caption = ctk.CTkLabel(
            frame, text=title, font=ctk.CTkFont(size=12), text_color=MUTED_TEXT
        )
        caption.grid(row=0, column=0, columnspan=3)

        minus = ctk.CTkButton(
            frame,
            text="-",
            width=32,
            height=32,
            fg_color=NEUTRAL_BUTTON,
            hover_color=NEUTRAL_BUTTON_HOVER,
            text_color=BUTTON_TEXT,
            command=on_minus,
        )
        value = ctk.CTkLabel(
            frame, text="0", width=60, font=ctk.CTkFont(size=24, weight="bold")
        )
        plus = ctk.CTkButton(
            frame,
            text="+",
            width=32,
            height=32,
            fg_color=ORANGE,
            hover_color=ORANGE_HOVER,
            text_color="#1A1A1A",
            command=on_plus,
        )
        minus.grid(row=1, column=0)
        value.grid(row=1, column=1)
        plus.grid(row=1, column=2)
        return value

    def _build_rate(self):
        """Build the diamond rate display. Returns the label showing the rate text."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=4, padx=(8, 20))

        caption = ctk.CTkLabel(
            frame, text="Diamond rate", font=ctk.CTkFont(size=12), text_color=MUTED_TEXT
        )
        caption.pack()
        value = ctk.CTkLabel(
            frame,
            text="",
            width=140,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ORANGE,
        )
        value.pack()
        return value

    def _change_kills(self, storage_function):
        self.kills = storage_function(self.map_name, self.species)
        self._refresh()

    def _change_diamonds(self, storage_function):
        self.diamonds = storage_function(self.map_name, self.species)
        self._refresh()

    def _toggle_pin(self):
        self.pinned = storage.toggle_pin(self.map_name, self.species)
        self._refresh()
        self.on_pin_change()

    def reload(self):
        """Re-read this animal's numbers from storage (used after editing in the focus view)."""
        entry = storage.get_entry(self.map_name, self.species)
        self.kills = entry["kills"]
        self.diamonds = entry["diamonds"]
        self._refresh()

    def _refresh(self):
        """Update everything on screen from the row's current numbers."""
        self.kills_label.configure(text=str(self.kills))
        self.diamonds_label.configure(text=str(self.diamonds))
        self.rate_label.configure(text=diamond_rate_text(self.kills, self.diamonds))
        if self.pinned:
            self.pin_button.configure(text="★", text_color=ORANGE)
        else:
            self.pin_button.configure(text="☆", text_color=MUTED_TEXT)