import re
from abc import ABC
from tkinter import ttk, END

from src.CharData.firearm_accessory import FirearmAccessory
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.app_data import pay_cash


class FirearmAccessoriesTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, show_race_mods=True)

        self.gunobj_dict = {}
        self.gun_box = ttk.Combobox(self, values=self.gunobj_dict.keys(), state="readonly")
        self.fill_combobox()

        self.gun_box.bind("<<ComboboxSelected>>", self.get_accobj)

        self.gun_box.grid(column=3, row=1)

    @property
    def library_source(self):
        return self.parent.game_data["Firearm Accessories"]

    @property
    def statblock_inventory(self):
        key = self.gun_box.get()
        if key == "Misc Accessories":
            return self.gunobj_dict[key]
        else:
            return self.gunobj_dict[key].properties["firearm_accessories"]

    @property
    def attributes_to_calculate(self):
        return []

    def fill_combobox(self):
        self.gunobj_dict = {}
        self.fill_stuff_with_accessories(self.statblock.inventory)
        self.gunobj_dict["Misc Accessories"] = self.statblock.misc_firearm_accessories
        self.gun_box["values"] = list(self.gunobj_dict.keys())

        self.gun_box.set("Misc Accessories")

    def fill_stuff_with_accessories(self, char_list):
        """Traverses entire character looking for stuff with an accessories property.
        :param char_list: something in self.statblock that could have something with accessories
        :type char_list: list
        """
        for node in char_list:
            # check for duplicate names
            key = node.name

            # count names that contain the key we want to use
            # we use regex to strip any dupe counts that
            dupe_count = 1
            for k in self.gunobj_dict.keys():
                k = re.sub(r"\s*\(\d+\)", "", k)
                if k == key:
                    dupe_count += 1

            # if we have more than one of the thing we want, add the dupe count to the key
            if dupe_count > 1:
                key += " ({})".format(dupe_count)

            if "firearm_accessories" in node.properties:
                self.gunobj_dict[key] = node  # .accessories

    def get_accobj(self, event):
        """Fills the inventory box with software from the selected memobj"""
        # clear list box
        self.inventory_list.delete(0, END)

        for obj in self.statblock_inventory:
            self.inventory_list.insert(END, obj.properties["name"])

    def buy_callback(self, selected):
        if pay_cash(selected.properties["cost"]):
            self.add_inv_item(selected)
        else:
            print("Not enough money!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock.inventory[self.inv_selected_item]

        # return cash value
        self.statblock.cash += selected_item.properties["cost"]

        self.remove_inv_item(self.inv_selected_item)

    @property
    def recurse_check_func(self):
        def firearm_accessories_recurse_check(val):
            return "cost" not in val.keys()

        return firearm_accessories_recurse_check

    @property
    def recurse_end_func(self):
        def firearm_accessories_recurse_end(key, val, iid):
            val["name"] = key
            self.tree_item_dict[iid] = FirearmAccessory(**val)

        return firearm_accessories_recurse_end

    def on_switch(self):
        self.fill_combobox()
        self.get_accobj(None)

    def load_character(self):
        self.on_switch()
