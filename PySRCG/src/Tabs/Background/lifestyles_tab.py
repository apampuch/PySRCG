import tkinter as tk
from abc import ABC
from tkinter import ttk

from src.Tabs.notebook_tab import NotebookTab


class LifestylesTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)

    def reload_data(self):
        pass

    def on_switch(self):
        pass

    def load_character(self):
        pass
