from abc import abstractmethod
from tkinter import ttk
import src.app_data as app_data

from src.Tabs.tab import Tab


class NotebookTab(ttk.Frame, Tab):
    """Base tab that other tabs inherit from"""

    def reload_data(self):
        """Doesn't need to be overridden because not all tabs need to handle data loading."""
        pass

    @abstractmethod
    def on_switch(self):
        pass

    @abstractmethod
    def load_character(self):
        pass

    def __init__(self, parent, name):
        super().__init__(parent)
        self.parent = parent
        self.name = name

    @property
    def character(self):
        return app_data.app_character

    @property
    def statblock(self):
        return self.character.statblock

    @property
    def gen_mode(self):
        return self.statblock.gen_mode

    @property
    def race(self):
        return self.statblock.race

