import src.app_data as app_data
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
        if len(app_data.app_character.statblock.decks) == 0:
            self.hide(self.tabs()[2])
        else:
            self.add(self.tabs()[2])
