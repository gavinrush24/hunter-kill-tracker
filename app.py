import customtkinter as ctk

from maps import get_map_names, get_species_for_map

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class KillTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hunter Kill Tracker")
        self.geometry("900x600")
        self.minsize(700, 400)

        # The window has two columns: a fixed sidebar (column 0)
        # and a content area that stretches to fill the rest (column 1).
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.map_buttons = {}
        self.selected_map = None

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
        self.content.grid_rowconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(
            self.content,
            text="",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        )
        self.header_label.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.animal_list = ctk.CTkScrollableFrame(self.content)
        self.animal_list.grid(row=1, column=0, sticky="nsew")
        self.animal_list.grid_columnconfigure(0, weight=1)

    def select_map(self, map_name):
        """Switch to a map: highlight its sidebar button and show its animals."""
        self.selected_map = map_name

        for name, button in self.map_buttons.items():
            if name == map_name:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color="transparent")

        self.header_label.configure(text=map_name)
        self._show_animals(map_name)

    def _show_animals(self, map_name):
        """Rebuild the scrolling list for one map (placeholder labels for now)."""
        for widget in self.animal_list.winfo_children():
            widget.destroy()

        for row, species in enumerate(get_species_for_map(map_name)):
            label = ctk.CTkLabel(
                self.animal_list,
                text=species,
                anchor="w",
                font=ctk.CTkFont(size=16),
            )
            label.grid(row=row, column=0, sticky="ew", padx=12, pady=10)


if __name__ == "__main__":
    app = KillTrackerApp()
    app.mainloop()