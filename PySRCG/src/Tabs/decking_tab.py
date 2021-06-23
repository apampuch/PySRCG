from src.CharData.deck import Deck
from src.Tabs.deck_buy_tab import DeckBuyTab
from src.Tabs.notebook_tab import NotebookTab
from src.Tabs.persona_tab import PersonaTab
from src.Tabs.programs_tab import ProgramsTab
from src.utils import recursive_treeview_fill, treeview_get, get_variables, calculate_attributes
from tkinter import *
from tkinter import ttk

import src.app_data as app_data


class DeckingTab(ttk.Notebook):

    def __init__(self, parent):
        super().__init__(parent)
        self.deck_tab = DeckBuyTab(parent, self.on_deck_change)
        self.programs_tab = ProgramsTab(parent, "Buy", "Sell")
        self.persona_tab = PersonaTab(parent)

        self.bind("<<NotebookTabChanged>>", app_data.window.on_tab_changed)

        self.add(self.deck_tab, text="Hardware")
        self.add(self.programs_tab, text="Software")
        self.add(self.persona_tab, text="Persona")

    def on_switch(self):
        self.deck_tab.on_switch()
        self.programs_tab.on_switch()
        self.persona_tab.on_switch()
        self.on_deck_change()

    def calculate_total(self):
        self.persona_tab.calculate_total()

    def load_character(self):
        self.deck_tab.load_character()
        self.programs_tab.load_character()
        self.persona_tab.load_character()
        self.on_deck_change()

    def on_deck_change(self):
        if len(app_data.app_character.statblock.decks) == 0:
            self.hide(self.tabs()[2])
        else:
            self.add(self.tabs()[2])
