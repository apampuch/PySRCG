from abc import ABC
from tkinter import *

from src import app_data
from src.CharData.augment import Cyberware
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


class CyberwareTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "CyberwareTab", show_cyberware_grades=True)

    @property
    def recurse_check_func(self):
        def cyberware_tab_recurse_check(val):
            return "essence" not in val.keys()

        return cyberware_tab_recurse_check

    @property
    def recurse_end_func(self):
        def cyberware_tab_recurse_end_callback(key, val, iid):
            # key is a string
            # val is a _dict from a json
            try:
                self.tree_item_dict[iid] = Cyberware(name=key, **val)
            except TypeError as e:
                print("Error with cyberware {}:".format(key))
                print(e)
                print()

        return cyberware_tab_recurse_end_callback

    @property
    def library_source(self):
        try:
            return self.parent.game_data["Augments"]["Cyberware"]
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.cyberware

    def buy_callback(self, selected):
        current_essence = self.statblock.essence

        # modify the item based on grade
        cyber: Cyberware = self.library_selected
        cyber.add_field("grade", str(self.grade_var.get()))

        cyber.properties["essence"] = self.calc_essence_cost(cyber, cyber.properties["grade"])
        cyber.properties["cost"] = int(self.calc_yen_cost(cyber, cyber.properties["grade"]))

        # if we have enough essence
        if cyber.properties["essence"] < current_essence:
            # if we have enough money
            if app_data.pay_cash(cyber.properties["cost"]):
                self.add_inv_item(cyber)
                self.calculate_total()
            else:
                print("Not enough cash!")
        else:
            print("Not enough essence left!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock_inventory[self.inv_selected_index]

        # return cash value
        self.statblock.add_cash(selected_item.properties["cost"])

        self.remove_inv_item(self.inv_selected_index)

        self.calculate_total()

    def calc_essence_cost(self, cyber, grade):
        essence = cyber.properties["essence"]

        if grade == "standard":
            pass
        elif grade == "alpha":
            essence *= 0.8
        elif grade == "beta":
            essence *= 0.6
        elif grade == "delta":
            essence *= 0.5
        else:
            raise ValueError("Invalid grade {}.".format(grade))

        return essence

    def calc_yen_cost(self, cyber, grade):
        cost = cyber.properties["cost"]

        if grade == "standard":
            pass
        elif grade == "alpha":
            cost *= 2
        elif grade == "beta":
            cost *= 4
        elif grade == "delta":
            cost *= 8
        else:
            raise ValueError("Invalid grade {}.".format(grade))

        return cost

    def fill_description_box(self, contents):
        """Clears the item description box and fills it with contents."""
        # temporarily unlock box, clear it, set the text, then re-lock it
        self.desc_box.config(state=NORMAL)
        self.desc_box.delete(1.0, END)
        self.desc_box.insert(END, contents)
        self.desc_box.config(state=DISABLED)

    def calculate_total(self):
        # unlike the other tabs places we directly manipulate the top bar
        # since this has nothing to do with the generation mode
        app_data.top_bar.update_karma_bar("{:.2f}".format(self.statblock.essence),
                                          self.statblock.base_attributes["essence"],
                                          "Augments Tab")

    def on_switch(self):
        self.calculate_total()

    def load_character(self):
        super().load_character()
        self.on_switch()
