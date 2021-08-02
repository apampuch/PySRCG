from abc import ABC

from tkinter import *
from tkinter import ttk

from src.app_data import pay_cash
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.CharData.gear import *

ATTRIBUTES_TO_CALCULATE = ["cost", "weight", "availability_rating", "availability_time", "street_index", "rating",
                           "transaction_limit"]  # find a better way to do this, maybe per-item?


class ItemsTab(ThreeColumnBuyTab, ABC):
    @property
    def inv_selected_item(self):
        """ID of the index of the selected item"""
        selection = self.inventory_list.curselection()
        if len(selection) is 0:
            return None
        return selection[-1]

    def __init__(self, parent):
        super().__init__(parent, show_quantity=True, show_race_mods=True)

    @property
    def recurse_check_func(self):
        def gear_tab_recurse_check(val):
            return "cost" not in val.keys()

        return gear_tab_recurse_check

    @property
    def recurse_end_func(self):
        def gear_tab_recurse_end_callback(key, val, iid):
            self.tree_item_dict[iid] = find_gear_by_dict(key, val)

        return gear_tab_recurse_end_callback

    def buy_callback(self, selected):
        # modify the item for any racial mods that have been selected
        if self.race_mod_var.get() == "Dwarf":
            selected.cost *= 1.1
            selected.cost = int(selected.cost)
            selected.other_fields["race_mod"] = "Dwarf"
        elif self.race_mod_var.get() == "Troll":
            selected.cost *= 1.25
            selected.cost = int(selected.cost)
            selected.other_fields["race_mod"] = "Troll"

        # get the amount by getting the value of the spinbox (always a string) and converting to int
        count = int(self.amount_spinbox.get())

        if pay_cash(selected.cost * count):
            self.add_inv_item(selected, count=count)
        else:
            print("Not enough money!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock.inventory[self.inv_selected_item]

        # return cash value
        self.statblock.cash += selected_item.cost

        self.remove_inv_item(self.inv_selected_item)

    @property
    def attributes_to_calculate(self):
        return ["cost", "weight", "availability_rating", "availability_time",
                "street_index", "rating", "transaction_limit"]

    @property
    def library_source(self):
        return self.parent.game_data["Items"]

    @property
    def statblock_inventory(self):
        return self.statblock.inventory

    def on_switch(self):
        pass

    def load_character(self):
        super().load_character()
        self.on_switch()
