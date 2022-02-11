from abc import ABC

from src.CharData.edge_flaw import EdgeFlaw
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


class EdgesFlawsTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)

    @property
    def library_source(self):
        try:
            return self.parent.game_data["Edges/Flaws"]
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.edges_flaws

    def buy_callback(self, selected):
        self.add_inv_item(selected)

    def sell_callback(self, selected_index):
        self.remove_inv_item(selected_index)

    @property
    def recurse_check_func(self):
        def check_func(val):
            return "cost" not in val.keys()

        return check_func

    @property
    def recurse_end_func(self):
        def end_func(key, val, iid):
            # add name to dict
            val["name"] = key
            self.tree_item_dict[iid] = EdgeFlaw(**val)

        return end_func

    def on_switch(self):
        pass

    def load_character(self):
        pass
