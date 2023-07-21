from abc import ABC
from tkinter.ttk import Labelframe

from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


# should be hidden if character is not an otaku
class ComplexFormsTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "ComplexFormsTab")

    @property
    def library_source(self):
        pass

    @property
    def statblock_inventory(self):
        pass

    def buy_callback(self, selected):
        pass

    def sell_callback(self, selected_index):
        pass

    @property
    def recurse_check_func(self):
        pass

    @property
    def recurse_end_func(self):
        pass

    def reload_data(self):
        pass

    def on_switch(self):
        pass

    def load_character(self):
        pass
