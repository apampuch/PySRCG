from tkinter import *
from tkinter import ttk

from src.Tabs.notebook_tab import NotebookTab

# list of attributes that we need to look for variables in, eg "Cost: rating * 500"
ATTRIBUTES_TO_CALCULATE = ["essence", "cost", "availability_rating", "availability_time"]
STRINGS_TO_IGNORE = []  # nyi


class BiowareTab(NotebookTab):
    def __init__(self, parent):
        super().__init__(parent, "BiowareTab")

        self.NYI_label = Label(self, {"text": "Not Yet Implemented"}).grid(column=0, row=0)

    def calculate_total(self):
        pass

    def on_switch(self):
        pass

    def load_character(self):
        pass
