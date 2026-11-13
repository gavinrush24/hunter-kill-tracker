import queue

import customtkinter as ctk

import settings
import storage
from animal_row import AnimalRow
from focus_view import FocusView
from hotkey_listener import HotkeyListener
from kill_events import KillEvent, resolve_target
from maps import get_map_names, get_species_for_map, is_valid_species
from theme import MUTED_TEXT, ORANGE

# How often (in milliseconds) the app checks for kills sent by background listeners.
EVENT_POLL_MS = 100

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class KillTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hunter Kill Tracker")
        self.geometry("1000x640")
        self.minsize(800, 560)

        # The window has two columns: a fixed sidebar (column 0)
        # and a content area that stretches to fill the rest (column 1).
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.map_buttons = {}
        self.rows = {}  # species name -> its AnimalRow, for the map being shown
        self.selected_map = None
        self.focus_view = None

        # Background listeners (hotkey, OCR) put KillEvents here; only the
        # main thread reads it, in _process_events. See kill_events.py for why.
        self.events = queue.Queue()

        self.settings = settings.load_settings()
        # pynput calls this from its own thread, so it only queues an event.
        self.hotkey_listener = HotkeyListener(
            self.settings["hotkey"],
            on_hotkey=lambda: self.events.put(KillEvent(source="hotkey")),
        )

        self._build_sidebar()
        self._build_content()
        self._bind_shortcuts()

        # Start on the first map in maps.json
        self.select_map(get_map_names()[0])

        if self.settings["auto_logging"]:
            self.auto_logging_switch.select()
            self._start_hotkey()

        self.after(EVENT_POLL_MS, self._process_events)

    def _toggle_auto_logging(self):
        """Turn the global hotkey on or off, and remember the choice."""
        on = bool(self.auto_logging_switch.get())
        if on:
            on = self._start_hotkey()
        else:
            self.hotkey_listener.stop()
            self.auto_logging_status.configure(text="")
        self.settings["auto_logging"] = on
        settings.save_settings(self.settings)

    def _start_hotkey(self):
        """Start the hotkey listener. Returns False (and turns the switch off) if it can't start."""
        try:
            self.hotkey_listener.start()
        except Exception as error:
            self.auto_logging_switch.deselect()
            self.auto_logging_status.configure(text=f"Hotkey unavailable: {error}")
            return False
        self.auto_logging_status.configure(
            text=f"Press {self.settings['hotkey'].upper()} in game to log a kill\nfor the animal in focus view"
        )
        return True

    def _process_events(self):
        """Apply every KillEvent waiting in the queue, then check again shortly."""
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            self._apply_kill_event(event)
        self.after(EVENT_POLL_MS, self._process_events)

    def _apply_kill_event(self, event):
        """Add one kill for the animal an event points at, and update the screen."""
        focused = self.focus_view.species if self.focus_view is not None else None
        target = resolve_target(event, self.selected_map, focused)
        if target is None:
            return
        map_name, species = target
        if not is_valid_species(map_name, species):
            return
        storage.add_kill(map_name, species)
        if self.focus_view is not None and self.focus_view.species == species:
            self.focus_view.reload()
        elif species in self.rows:
            self.rows[species].reload()

    def _bind_shortcuts(self):
        """Set up the keyboard shortcuts. They only do something while the focus view is open."""
        shortcuts = {
            "<Escape>": lambda view: self.close_focus(),
            "<Up>": lambda view: view.add_kill(),
            "<Down>": lambda view: view.remove_kill(),
            "<Right>": lambda view: view.add_diamond(),
            "<Left>": lambda view: view.remove_diamond(),
        }
        for key, action in shortcuts.items():
            self.bind(key, lambda event, action=action: self._run_focus_shortcut(action))

    def _run_focus_shortcut(self, action):
        """Run a shortcut's action on the focus view, but only if the focus view is open."""
        if self.focus_view is not None:
            action(self.focus_view)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        # Keep the sidebar exactly 240 wide instead of shrinking to fit its contents.
        self.sidebar.pack_propagate(False)

        title = ctk.CTkLabel(
            self.sidebar, text="Reserves", font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(padx=20, pady=(24, 12), anchor="w")

        # Auto-logging controls sit at the bottom of the sidebar. They're packed
        # before the map list so the list's expand=True can't push them off screen.
        self.auto_logging_status = ctk.CTkLabel(
            self.sidebar,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=MUTED_TEXT,
            justify="left",
            wraplength=210,
        )
        self.auto_logging_status.pack(side="bottom", padx=20, pady=(0, 16), anchor="w")
        self.auto_logging_switch = ctk.CTkSwitch(
            self.sidebar,
            text=f"Auto-logging ({self.settings['hotkey'].upper()})",
            progress_color=ORANGE,
            command=self._toggle_auto_logging,
        )
        self.auto_logging_switch.pack(side="bottom", padx=20, pady=(8, 4), anchor="w")

        # With 19 reserves the buttons are taller than the window, so they
        # live in a scrollable frame under the fixed "Reserves" title.
        self.map_list = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent", corner_radius=0
        )
        self.map_list.pack(fill="both", expand=True, padx=(4, 0), pady=(0, 8))

        for map_name in get_map_names():
            button = ctk.CTkButton(
                self.map_list,
                text=map_name,
                anchor="w",
                fg_color="transparent",
                border_width=0,
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda name=map_name: self.select_map(name),
            )
            button.pack(fill="x", padx=8, pady=2)
            self.map_buttons[map_name] = button

    def _build_content(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)

        self.header_label = ctk.CTkLabel(
            self.content,
            text="",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        )
        self.header_label.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        # A thin orange line under the title.
        accent = ctk.CTkFrame(self.content, height=3, corner_radius=2, fg_color=ORANGE)
        accent.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self.animal_list = ctk.CTkScrollableFrame(self.content)
        self.animal_list.grid(row=2, column=0, sticky="nsew")
        self.animal_list.grid_columnconfigure(0, weight=1)

    def select_map(self, map_name):
        """Switch to a map: highlight its sidebar button and show its animals."""
        self.selected_map = map_name
        for name, button in self.map_buttons.items():
            if name == map_name:
                button.configure(
                    fg_color=("gray75", "gray25"), border_width=2, border_color=ORANGE
                )
            else:
                button.configure(fg_color="transparent", border_width=0)
        self.header_label.configure(text=map_name)
        self._show_animals(map_name)

    def _show_animals(self, map_name):
        """Rebuild the scrolling list with one row per animal on this map."""
        for widget in self.animal_list.winfo_children():
            widget.destroy()
        self.rows = {}
        for species in get_species_for_map(map_name):
            self.rows[species] = AnimalRow(
                self.animal_list,
                map_name,
                species,
                on_open=self.open_focus,
                on_pin_change=self.arrange_rows,
            )
        self.arrange_rows()

    def arrange_rows(self):
        """Place the rows in order: pinned animals first, the rest in their usual order."""
        species_in_order = sorted(
            self.rows,
            key=lambda species: not storage.get_entry(self.selected_map, species)["pinned"],
        )
        for position, species in enumerate(species_in_order):
            self.rows[species].grid(row=position, column=0, sticky="ew")

    def open_focus(self, species):
        """Hide the sidebar and list, and show one animal full-window."""
        self.sidebar.grid_remove()
        self.content.grid_remove()
        self.focus_view = FocusView(
            self, self.selected_map, species, on_back=self.close_focus
        )
        self.focus_view.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def close_focus(self):
        """Go back to the list, and update that animal's row with any changes."""
        species = self.focus_view.species
        self.focus_view.destroy()
        self.focus_view = None
        self.sidebar.grid()
        self.content.grid()
        self.rows[species].reload()


if __name__ == "__main__":
    app = KillTrackerApp()
    app.mainloop()