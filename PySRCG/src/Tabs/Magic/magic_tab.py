from tkinter import ttk

from src import app_data
from src.Tabs.Magic.magic_background_tab import MagicBackgroundTab
from src.Tabs.Magic.powers_tab import PowersTab
from src.Tabs.Magic.spells_tab import SpellsTab


class MagicTab(ttk.Notebook):
    def __init__(self, parent):

        super().__init__(parent)
        self.background_tab = MagicBackgroundTab(parent)
        self.spells_tab = SpellsTab(parent)
        self.powers_tab = PowersTab(parent)

        self.bind("<<NotebookTabChanged>>", app_data.window.on_tab_changed)

        self.add(self.background_tab, text="Background")
        self.add(self.spells_tab, text="Spells")
        self.add(self.powers_tab, text="Powers")

    def show_hide_tabs(self, awakened, tradition):
        # if no tradition, hide both tabs
        if tradition is None:
            self.tab(".!app.!powerstab", state="hidden")
            self.tab(".!app.!spellstab", state="hidden")
        # if an adept, always show powers
        elif tradition.name == "Adept":
            self.tab(".!app.!powerstab", state="normal")

            # if aspected, hide spells
            if awakened == "Aspected":
                self.tab(".!app.!spellstab", state="hidden")

            # otherwise, show spells
            else:
                self.tab(".!app.!spellstab", state="normal")

        # otherwise, hide powers and show spells
        else:
            self.tab(".!app.!powerstab", state="hidden")
            self.tab(".!app.!spellstab", state="normal")

    def on_switch(self):
        self.background_tab.on_switch()
        self.spells_tab.on_switch()
        self.powers_tab.on_switch()

    # Do I need this?
    def calculate_total(self):
        self.spells_tab.calculate_total()
        self.powers_tab.calculate_total()

    def load_character(self):
        self.background_tab.load_character()
        self.spells_tab.load_character()
        self.powers_tab.load_character()
