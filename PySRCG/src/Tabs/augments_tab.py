from tkinter import ttk

from src.Tabs.bioware_tab import BiowareTab
from src.Tabs.cyberware_tab import CyberwareTab

# list of attributes that we need to look for variables in, eg "Cost: rating * 500"
ATTRIBUTES_TO_CALCULATE = ["essence", "cost", "availability_rating", "availability_time"]
STRINGS_TO_IGNORE = []  # nyi


class AugmentsTab(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.cyberware_tab = CyberwareTab(parent)
        self.bioware_tab = BiowareTab(parent)

        self.add(self.cyberware_tab, text="Cyberware")
        self.add(self.bioware_tab, text="Bioware")

    def on_switch(self):
        self.cyberware_tab.on_switch()
        self.bioware_tab.on_switch()

    def load_character(self):
        self.cyberware_tab.load_character()
        self.bioware_tab.load_character()

    def calculate_total(self):
        self.cyberware_tab.calculate_total()
        self.bioware_tab.calculate_total()




