from abc import ABC

from src import app_data
from src.CharData.echo import Echo
from src.GenModes.finalized import Finalized
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.adjustment import Adjustment


class SubmersionTab(ThreeColumnBuyTab, ABC):
    """
    Tab to handle Otaku submersions.
    Only shows when Finalized.
    """
    def __init__(self, parent):
        super(SubmersionTab, self).__init__(parent, "SubmersionTab")

    def update_karma_bar(self):
        progress_bar = app_data.top_bar.karma_bar
        progress_bar.configure(variable=self.gen_mode.adjustments, maximum=self.gen_mode.good_karma.get())

    @property
    def library_source(self):
        try:
            return app_data.game_data["Echoes"]
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.echoes

    def buy_callback(self, selected):
        if type(self.gen_mode) is not Finalized:
            raise ValueError("Must be Finalized to use this tab!")
        submersion_cost = 10 + 2 * (len(self.statblock.echoes) + 1)

        if self.statblock.gen_mode.point_purchase_allowed(submersion_cost, None):
            def undo():
                return  # do nothing, deletion is handled in tab

            adjustment = Adjustment(submersion_cost, "add_echo_" + selected.name, undo, "Add echo")
            self.gen_mode.add_adjustment(adjustment)

            self.add_inv_item(selected)

    def sell_callback(self, selected_index):
        selected_echo = self.statblock.echoes[selected_index]
        if "add_echo_" + selected_echo.properties["name"] in self.gen_mode.adjustments:
            self.gen_mode.undo("add_echo_" + selected_echo.properties["name"])
            self.remove_inv_item(selected_index)
        else:
            print("Can't remove that, no adjustment made.")

    @property
    def recurse_check_func(self):
        def echo_recurse_check(val):
            return "no_duplicates" not in val.keys()

        return echo_recurse_check

    @property
    def recurse_end_func(self):
        def echo_recurse_end(key, val, iid):
            val["name"] = key
            self.tree_item_dict[iid] = Echo(**val)

        return echo_recurse_end

    def on_switch(self):
        super().on_switch()
        self.statblock.gen_mode.update_total(None, None)

    def load_character(self):
        super().load_character()
