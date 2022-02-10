from abc import ABC

from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


class EdgesFlawsTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)

    @property
    def library_source(self):
        try:
            return {}
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return {}

    def buy_callback(self, selected):
        pass

    def sell_callback(self, selected_index):
        pass

    @property
    def recurse_check_func(self):
        return {}

    @property
    def recurse_end_func(self):
        return {}

    def on_switch(self):
        pass

    def load_character(self):
        pass
