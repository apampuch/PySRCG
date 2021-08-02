from tkinter import ttk

from src import app_data
from src.Tabs.ammo_tab import AmmoTab
from src.Tabs.items_tab import ItemsTab


class GearTab(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.items_tab = ItemsTab(parent)
        self.ammo_tab = AmmoTab(parent)

        self.bind("<<NotebookTabChanged>>", app_data.window.on_tab_changed)

        self.add(self.items_tab, text="Items")
        self.add(self.ammo_tab, text="Ammo")

    def on_switch(self):
        self.items_tab.on_switch()
        self.ammo_tab.on_switch()

    def load_character(self):
        self.items_tab.load_character()
        self.ammo_tab.load_character()
