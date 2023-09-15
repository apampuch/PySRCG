import src.app_data as app_data
from src.GenModes.finalized import Finalized
from src.Tabs.container_tab import ContainerTab


class DeckingTab(ContainerTab):
    def __init__(self, parent):
        super().__init__(parent, "DeckingTab")

    def load_character(self):
        super().load_character()
        self.on_deck_change()

    def on_deck_change(self):
        """
        This function shows the persona tab when the character has decks, and hides it when the character doesn't.
        """
        if len(app_data.app_character.statblock.all_decks()) == 0:
            self.hide(self.tabs()[2])
        else:
            self.add(self.tabs()[2])

    def show_hide_tabs(self, otaku):
        if otaku:
            self.add(self.tabs()[3])
            self.add(self.tabs()[4])
            # this should never be unset after being finalized, no need for logic here
            if type(app_data.app_character.statblock.gen_mode) == Finalized:
                self.add(self.tabs()[5])
        else:
            self.hide(self.tabs()[3])
            self.hide(self.tabs()[4])
            self.hide(self.tabs()[5])

    def on_switch(self):
        super().on_switch()
        self.on_deck_change()
