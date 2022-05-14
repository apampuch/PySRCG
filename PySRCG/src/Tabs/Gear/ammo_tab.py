from abc import ABC

from tkinter import *

from src.CharData.gear import find_gear_by_dict, Gear
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.app_data import pay_cash


class AmmoTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, show_quantity=True, buy_from_list=True)

    @staticmethod
    def name_for_list(x):
        return f"{x.properties['name']} ({x.properties['count']})"

    @property
    def library_source(self):
        try:
            return self.parent.game_data["Ammunition"]
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.ammunition

    def buy_callback(self, selected):
        # get the amount by getting the value of the spinbox (always a string) and converting to int
        count = int(self.amount_spinbox.get())

        # add count property to the item if it doesn't exist yet
        if "count" not in selected.properties.keys():
            selected.properties["count"] = count

        if pay_cash(selected.properties["cost"] * count):
            exists_index = -1
            for i in range(0, len(self.statblock_inventory)):
                if self.statblock_inventory[i].name == selected.name:
                    exists_index = i
                    break
            if exists_index >= 0:
                self.statblock_inventory[exists_index].properties["count"] += count
                # update label and report box
                self.update_inventory_text_at_index(exists_index, f"{selected.name} ({self.statblock_inventory[exists_index].properties['count']})")
                self.fill_description_box(self.statblock_inventory[exists_index].report())
            else:
                self.add_inv_item(selected)
        else:
            print("Not enough money!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock.ammunition[selected_index]
        count = min(selected_item.properties["count"], int(self.amount_spinbox.get()))

        # return cash value
        self.statblock.add_cash(selected_item.properties["cost"] * count)

        # remove amount or delete if all would be removed
        if count == selected_item.properties["count"]:
            self.remove_inv_item(self.inv_selected_index)
        elif count < selected_item.properties["count"]:
            selected_item.properties["count"] -= count
            self.update_inventory_text_at_index(selected_index, f"{selected_item.name} ({self.statblock_inventory[selected_index].properties['count']})")
            self.fill_description_box(self.statblock_inventory[selected_index].report())
        else:
            item_count = selected_item.properties["count"]
            raise ValueError(f"{selected_item.name} has count of {item_count}, trying to remove {count}.")

    @property
    def recurse_check_func(self):
        def gear_tab_recurse_check(val):
            return "cost" not in val.keys()

        return gear_tab_recurse_check

    @property
    def recurse_end_func(self):
        def gear_tab_recurse_end_callback(key, val, iid):
            # add name to val
            val["name"] = key
            self.tree_item_dict[iid] = Gear(**val)

        return gear_tab_recurse_end_callback

    def on_switch(self):
        pass

    def load_character(self):
        self.inventory_list.delete(0, END)
        for item in self.statblock_inventory:
            self.inventory_list.insert(END, f"{item.name} ({item.properties['count']})")
