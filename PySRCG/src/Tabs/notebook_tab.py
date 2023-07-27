from tkinter import ttk
import src.app_data as app_data
import abc


class NotebookTab(ttk.Frame):
    """Base tab that other tabs inherit from"""
    def __init__(self, parent, name):
        super().__init__(parent)
        self.parent = parent
        self.name = name

    def karma_bar_handler(self):
        pass

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

    @abc.abstractmethod
    def reload_data(self):
        pass

    @abc.abstractmethod
    def on_switch(self):
        """Called on tab switch."""
        pass

    @abc.abstractmethod
    def load_character(self):
        """Called on character load."""
        pass
