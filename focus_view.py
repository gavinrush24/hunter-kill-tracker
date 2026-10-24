import customtkinter as ctk
from tkinter import messagebox

import storage
from badges import get_badge_image
from stats import diamond_rate_text
from theme import (
    ORANGE,
    ORANGE_HOVER,
    MUTED_TEXT,
    NEUTRAL_BUTTON,
    NEUTRAL_BUTTON_HOVER,
    BUTTON_TEXT,
)

BIG_BADGE_SIZE = 180


class FocusView(ctk.CTkFrame):
    """A full-window view of one animal, with big counters for grinding."""

    def __init__(self, parent, map_name, species, on_back):
        super().__init__(parent, fg_color="transparent")
        self.map_name = map_name
        self.species = species

        entry = storage.get_entry(map_name, species)
        self.kills = entry["kills"]
        self.diamonds = entry["diamonds"]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        back_button = ctk.CTkButton(
            self,
            text="←  Back to list",
            width=140,
            height=36,
            fg_color=NEUTRAL_BUTTON,
            hover_color=NEUTRAL_BUTTON_HOVER,
            text_color=BUTTON_TEXT,
            command=on_back,
        )
        back_button.grid(row=0, column=0, sticky="w", padx=20, pady=20)

        # Everything else sits in one frame in the middle of the window.
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=1, column=0)

        self._build_header(center)
        self._build_counters(center)

        reset_button = ctk.CTkButton(
        center,
        text="Reset animal",
        width=140,
        height=36,
        fg_color=NEUTRAL_BUTTON,
        hover_color=NEUTRAL_BUTTON_HOVER,
        text_color=BUTTON_TEXT,
        command=self.confirm_reset,
        )
        reset_button.grid(row=4, column=0, pady=(24, 0))

        # A reminder of the keyboard shortcuts (they are set up in app.py).
        hint = ctk.CTkLabel(
            self,
            text="Esc  back        ↑ ↓  kills        → ←  diamonds",
            font=ctk.CTkFont(size=13),
            text_color=MUTED_TEXT,
        )
        hint.grid(row=2, column=0, pady=(0, 20))

        self._refresh()

    def _build_header(self, parent):
        # A placeholder badge for now: this is where the badge image will go.
        badge = ctk.CTkFrame(
            parent,
            width=BIG_BADGE_SIZE,
            height=BIG_BADGE_SIZE,
            corner_radius=24,
            border_width=3,
            border_color=ORANGE,
            fg_color=("gray85", "gray20"),
        )
        badge.grid(row=0, column=0, pady=(0, 16))
        badge.grid_propagate(False)
        badge.grid_rowconfigure(0, weight=1)
        badge.grid_columnconfigure(0, weight=1)

        image = get_badge_image(self.species, BIG_BADGE_SIZE)
        if image is not None:
            badge.configure(border_width=0, fg_color="transparent")
            label = ctk.CTkLabel(badge, text="", image=image)
        else:
            label = ctk.CTkLabel(
                badge, text=self.species[0], font=ctk.CTkFont(size=90, weight="bold")
            )
        label.grid(row=0, column=0)

        name = ctk.CTkLabel(
            parent, text=self.species, font=ctk.CTkFont(size=34, weight="bold")
        )
        name.grid(row=1, column=0)

        map_label = ctk.CTkLabel(
            parent,
            text=self.map_name,
            font=ctk.CTkFont(size=14),
            text_color=MUTED_TEXT,
        )
        map_label.grid(row=2, column=0, pady=(0, 24))

    def _build_counters(self, parent):
        counters = ctk.CTkFrame(parent, fg_color="transparent")
        counters.grid(row=3, column=0)

        self.kills_label = self._build_counter(
            counters,
            column=0,
            title="Kills",
            on_minus=self.remove_kill,
            on_plus=self.add_kill,
        )
        self.diamonds_label = self._build_counter(
            counters,
            column=1,
            title="Diamonds",
            on_minus=self.remove_diamond,
            on_plus=self.add_diamond,
        )
        self.rate_label = self._build_rate(counters, column=2)

    def _build_counter(self, parent, column, title, on_minus, on_plus):
        """Build a big titled counter with - and + buttons. Returns the number label."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, padx=28, sticky="n")

        caption = ctk.CTkLabel(
            frame, text=title, font=ctk.CTkFont(size=16), text_color=MUTED_TEXT
        )
        caption.grid(row=0, column=0, columnspan=2)

        value = ctk.CTkLabel(
            frame, text="0", width=170, font=ctk.CTkFont(size=64, weight="bold")
        )
        value.grid(row=1, column=0, columnspan=2, pady=(0, 8))

        minus = ctk.CTkButton(
            frame,
            text="-",
            width=64,
            height=48,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color=NEUTRAL_BUTTON,
            hover_color=NEUTRAL_BUTTON_HOVER,
            text_color=BUTTON_TEXT,
            command=on_minus,
        )
        plus = ctk.CTkButton(
            frame,
            text="+",
            width=64,
            height=48,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color=ORANGE,
            hover_color=ORANGE_HOVER,
            text_color="#1A1A1A",
            command=on_plus,
        )
        minus.grid(row=2, column=0, padx=4)
        plus.grid(row=2, column=1, padx=4)
        return value

    def _build_rate(self, parent, column):
        """Build the diamond rate display. Returns the label showing the rate text."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, padx=28, sticky="n")

        caption = ctk.CTkLabel(
            frame,
            text="Diamond rate",
            font=ctk.CTkFont(size=16),
            text_color=MUTED_TEXT,
        )
        caption.pack()

        value = ctk.CTkLabel(
            frame,
            text="",
            width=210,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=ORANGE,
        )
        value.pack(pady=(18, 0))
        return value

    # These four are used by the on-screen buttons and by the keyboard shortcuts in app.py.
    def add_kill(self):
        self._change_kills(storage.add_kill)

    def remove_kill(self):
        self._change_kills(storage.remove_kill)

    def add_diamond(self):
        self._change_diamonds(storage.add_diamond)

    def remove_diamond(self):
        self._change_diamonds(storage.remove_diamond)

    def confirm_reset(self):
        """Ask first, then reset this animal's kills and diamonds to zero."""
        answer = messagebox.askyesno(
            "Reset animal",
            f"Reset {self.species} to 0 kills and 0 diamonds?\n\nThis can't be undone.",
        )
        if answer:
            storage.reset_animal(self.map_name, self.species)
            self.kills = 0
            self.diamonds = 0
            self._refresh()

    def _change_kills(self, storage_function):
        self.kills = storage_function(self.map_name, self.species)
        self._refresh()

    def _change_diamonds(self, storage_function):
        self.diamonds = storage_function(self.map_name, self.species)
        self._refresh()

    def _refresh(self):
        """Update everything on screen from the view's current numbers."""
        self.kills_label.configure(text=str(self.kills))
        self.diamonds_label.configure(text=str(self.diamonds))
        self.rate_label.configure(text=diamond_rate_text(self.kills, self.diamonds))