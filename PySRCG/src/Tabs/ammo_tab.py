from abc import ABC

from tkinter import *

from src.CharData.gear import find_gear_by_dict
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.app_data import pay_cash


class AmmoTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, show_quantity=True, buy_from_list=True)

    @property
    def library_source(self):
        return self.parent.game_data["Ammunition"]

    @property
    def statblock_inventory(self):
        return self.statblock.ammunition

    @property
    def attributes_to_calculate(self):
        return []

    def buy_callback(self, selected):
        # get the amount by getting the value of the spinbox (always a string) and converting to int
        count = int(self.amount_spinbox.get())

        # add count property to the item if it doesn't exist yet
        if "count" not in selected.other_fields.keys():
            selected.other_fields["count"] = count

        if pay_cash(selected.cost * count):
            exists_index = -1
            for i in range(0, len(self.statblock_inventory)):
                if self.statblock_inventory[i].name == selected.name:
                    exists_index = i
                    break
            if exists_index >= 0:
                self.statblock_inventory[exists_index].other_fields["count"] += count
                # update label and report box
                self.update_inventory_text_at_index(exists_index, f"{selected.name} ({self.statblock_inventory[exists_index].other_fields['count']})")
                self.fill_description_box(self.statblock_inventory[exists_index].report())
            else:
                self.add_inv_item(selected, listbox_string=lambda x: f"{x.name} ({x.other_fields['count']})")
        else:
            print("Not enough money!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock.ammunition[selected_index]
        count = min(selected_item.other_fields["count"], int(self.amount_spinbox.get()))

        # return cash value
        self.statblock.cash += selected_item.cost * count

        # remove amount or delete if all would be removed
        if count == selected_item.other_fields["count"]:
            self.remove_inv_item(self.inv_selected_item)
        elif count < selected_item.other_fields["count"]:
            selected_item.other_fields["count"] -= count
            self.update_inventory_text_at_index(selected_index, f"{selected_item.name} ({self.statblock_inventory[selected_index].other_fields['count']})")
            self.fill_description_box(self.statblock_inventory[selected_index].report())
        else:
            item_count = selected_item.other_fields["count"]
            raise ValueError(f"{selected_item.name} has count of {item_count}, trying to remove {count}.")

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

    def on_switch(self):
        pass

    def load_character(self):
        self.inventory_list.delete(0, END)
        for item in self.statblock_inventory:
            self.inventory_list.insert(END, f"{item.name} ({item.other_fields['count']})")
