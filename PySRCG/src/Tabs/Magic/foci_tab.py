from abc import ABC
from tkinter import *

from src import app_data
from src.CharData.focus import Focus
from src.GenModes.finalized import Finalized
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.app_data import pay_cash


class FociTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "FociTab")

        self.bind_button = Button(self, text="Bind Focus", command=self.bind_focus)
        self.unbind_button = Button(self, text="Unbind Focus", command=self.unbind_focus)

        self.bind_button.grid(column=3, row=1)
        self.unbind_button.grid(column=4, row=1)

    @staticmethod
    def name_for_list(x):
        if x.properties["bound"]:
            return f"{x.name} (BOUND)"
        else:
            return x.name

    @property
    def library_source(self):
        try:
            return app_data.game_data["Foci"]
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.foci

    def buy_callback(self, selected):
        if pay_cash(selected.properties["cost"]):
            self.add_inv_item(selected)
        else:
            print("Not enough money!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock_inventory[self.inv_selected_index]

        # return cash value
        self.statblock.add_cash(selected_item.properties["cost"])

        self.remove_inv_item(self.inv_selected_index)

    @property
    def recurse_check_func(self):
        return lambda x: "karma_cost" not in x.keys()

    @property
    def recurse_end_func(self):
        def foci_tab_recurse_end_callback(key, val, iid):
            # add name to dict
            val["name"] = key
            self.tree_item_dict[iid] = Focus(**val)

        return foci_tab_recurse_end_callback

    def bind_focus(self):
        if len(self.inventory_list.curselection()) == 0:
            return

        # check if bound already
        if self.list_selected.properties["bound"]:
            print("Already bound!")
            return

        # check if enough karma
        if self.statblock.gen_mode.point_purchase_allowed(self.list_selected.properties["karma_cost"], "magic"):
            self.list_selected.properties["bound"] = True
            if type(self.statblock.gen_mode) == Finalized:
                self.statblock.gen_mode.adjustments.make_and_add(
                    self.list_selected.properties["karma_cost"], "bind_focus")

            self.on_switch()
        else:
            print("Not enough karma!")

    def unbind_focus(self):
        if len(self.inventory_list.curselection()) == 0:
            return

        if not self.list_selected.properties["bound"]:
            print("Already unbound!")
            return

        self.list_selected.properties["bound"] = False
        if type(self.statblock.gen_mode) == Finalized:
            self.statblock.gen_mode.adjustments.undo_latest("bind_focus")
        self.on_switch()

    def get_total(self):
        total = 0

        for spell in self.statblock.spells:
            total += spell.properties["force"]

        for focus in self.statblock.foci:
            if focus.properties["bound"]:
                total += focus.properties["karma_cost"]

        return total

    def calculate_total(self):
        """Totals all spell points and updates the top karma bar."""
        self.statblock.gen_mode.update_total(self.get_total(), "magic")

    def on_switch(self):
        super().on_switch()
        self.calculate_total()

    def load_character(self):
        super().load_character()
