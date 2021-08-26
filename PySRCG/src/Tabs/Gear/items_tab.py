from abc import ABC

from src.app_data import pay_cash
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.CharData.gear import *


class ItemsTab(ThreeColumnBuyTab, ABC):
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
            # add name to dict
            val["name"] = key
            self.tree_item_dict[iid] = Gear(**val)

        return gear_tab_recurse_end_callback

    def buy_callback(self, selected):
        # modify the item for any racial mods that have been selected
        if self.race_mod_var.get() == "Dwarf":
            selected.properties["cost"] *= 1.1
            selected.properties["cost"] = int(selected.properties["cost"])
            selected.properties["race_mod"] = "Dwarf"
        elif self.race_mod_var.get() == "Troll":
            selected.properties["cost"] *= 1.25
            selected.properties["cost"] = int(selected.properties["cost"])
            selected.properties["race_mod"] = "Troll"

        # get the amount by getting the value of the spinbox (always a string) and converting to int
        count = int(self.amount_spinbox.get())

        if pay_cash(selected.properties["cost"] * count):
            self.add_inv_item(selected, count=count)
        else:
            print("Not enough money!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock_inventory[self.inv_selected_item]

        # return cash value
        self.statblock.cash += selected_item.properties["cost"]

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
