from abc import ABC

from src.CharData.augment import Bioware
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


class BiowareTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "BiowareTab")

    @property
    def library_source(self):
        try:
            return self.parent.game_data["Bioware"]
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.bioware

    def buy_callback(self, selected):
        pass

    def sell_callback(self, selected_index):
        pass

    @property
    def recurse_check_func(self):
        def bioware_tab_recurse_check(val):
            return "bio_index" not in val.keys()

        return bioware_tab_recurse_check

    @property
    def recurse_end_func(self):
        def bioware_tab_recurse_end_callback(key, val, iid):
            # key is a string
            # val is a _dict from a json
            try:
                self.tree_item_dict[iid] = Bioware(name=key, **val)
            except TypeError as e:
                print("Error with bioware {}:".format(key))
                print(e)
                print()

        return bioware_tab_recurse_end_callback

    def calculate_total(self):
        pass

    def on_switch(self):
        self.calculate_total()

    def load_character(self):
        super().load_character()
        self.on_switch()
