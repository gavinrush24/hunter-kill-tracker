import customtkinter as ctk

import storage
from animal_row import AnimalRow
from focus_view import FocusView
from maps import get_map_names, get_species_for_map
from theme import ORANGE

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

        self._build_sidebar()
        self._build_content()

        # Start on the first map in maps.json
        self.select_map(get_map_names()[0])

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        title = ctk.CTkLabel(
            self.sidebar, text="Reserves", font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(padx=20, pady=(24, 12), anchor="w")

        for map_name in get_map_names():
            button = ctk.CTkButton(
                self.sidebar,
                text=map_name,
                anchor="w",
                fg_color="transparent",
                border_width=0,
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda name=map_name: self.select_map(name),
            )
            button.pack(fill="x", padx=12, pady=2)
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