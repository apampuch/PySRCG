from src.Tabs.Decking.complex_forms_tab import ComplexFormsTab
from src.Tabs.Decking.deck_buy_tab import DeckBuyTab
from src.Tabs.Decking.otaku_tab import OtakuTab
from src.Tabs.Decking.persona_tab import PersonaTab
from src.Tabs.Decking.programs_tab import ProgramsTab
from tkinter import ttk

import src.app_data as app_data


class DeckingTab(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.name = "DeckingTab"
        self.deck_tab = DeckBuyTab(parent, [self.on_deck_change], [self.on_deck_change])
        self.programs_tab = ProgramsTab(parent, "Buy", "Sell")
        self.persona_tab = PersonaTab(parent)
        self.otaku_tab = OtakuTab(parent)
        self.complex_forms_tab = ComplexFormsTab(parent)

        self.bind("<<NotebookTabChanged>>", app_data.window.on_tab_changed)

        self.add(self.deck_tab, text="Hardware")
        self.add(self.programs_tab, text="Software")
        self.add(self.persona_tab, text="Persona")
        self.add(self.otaku_tab, text="Otaku")
        self.add(self.complex_forms_tab, text="Complex Forms")

    def on_switch(self):
        self.deck_tab.on_switch()
        self.programs_tab.on_switch()
        self.persona_tab.on_switch()
        self.otaku_tab.on_switch()
        self.complex_forms_tab.on_switch()
        self.on_deck_change()

    def calculate_total(self):
        self.persona_tab.calculate_total()
        self.complex_forms_tab.calculate_total()

    def reload_data(self):
        self.deck_tab.reload_data()
        self.programs_tab.reload_data()

    def load_character(self):
        self.deck_tab.load_character()
        self.programs_tab.load_character()
        self.persona_tab.load_character()
        self.otaku_tab.load_character()
        self.complex_forms_tab.load_character()
        self.on_deck_change()

    def on_deck_change(self):
        """
        This function shows the persona tab when the character has decks, and hides it when the character doesn't.
        """
        if len(app_data.app_character.statblock.decks) == 0:
            self.hide(self.tabs()[2])
        else:
            self.add(self.tabs()[2])
