import customtkinter as ctk

from storage import load_counts, add_kill
from species import SPECIES

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class KillCounterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hunter Kill Tracker")
        self.geometry("320x220")

        self.species = SPECIES[0]
        self.count = load_counts().get(self.species, 0)

        self.name_label = ctk.CTkLabel(
            self, text=self.species, font=ctk.CTkFont(size=20, weight="bold")
        )
        self.name_label.pack(pady=(30, 10))

        self.count_label = ctk.CTkLabel(
            self, text=str(self.count), font=ctk.CTkFont(size=48, weight="bold")
        )
        self.count_label.pack()

        self.add_button = ctk.CTkButton(
            self, text="+1 Kill", command=self.on_add_kill
        )
        self.add_button.pack(pady=20)

    def on_add_kill(self):
        self.count = add_kill(self.species)
        self.count_label.configure(text=str(self.count))


if __name__ == "__main__":
    app = KillCounterApp()
    app.mainloop()