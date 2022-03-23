from abc import ABC

from src import app_data
from src.CharData.edge_flaw import EdgeFlaw
from src.GenModes.finalized import Finalized
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


class EdgesFlawsTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)
        self.no_duplicates = True

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
        self.calculate_total()

    def sell_callback(self, selected_index):
        self.remove_inv_item(selected_index)
        self.calculate_total()

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

    def calculate_total(self):
        if type(self.gen_mode) is not Finalized:
            total = 0
            for edge_flaw in self.statblock_inventory:
                total += edge_flaw.properties["cost"]

            self.gen_mode.cur_edge_flaw_points.set(total)

            app_data.top_bar.karma_fraction.set("{}".format(self.statblock.gen_mode.cur_edge_flaw_points.get()))

    def on_switch(self):
        pass

    def load_character(self):
        super().load_character()
        self.calculate_total()
        self.on_switch()
