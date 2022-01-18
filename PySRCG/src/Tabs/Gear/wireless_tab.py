import re
from abc import ABC
from tkinter import ttk, END

from src.CharData.WirelessAccessory import WirelessAccessory
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.app_data import pay_cash


class WirelessTab(ThreeColumnBuyTab):
    def __init__(self, parent):
        super().__init__(parent)

        self.wireless_obj_dict = {}
        self.wireless_box = ttk.Combobox(self, values=self.wireless_obj_dict.keys(), state="readonly")
        self.fill_combobox()

        self.wireless_box.bind("<<ComboboxSelected>>", self.get_accobj)

        self.wireless_box.grid(column=3, row=1)

    @property
    def library_source(self):
        return self.parent.game_data["Wireless Accessories"]

    @property
    def statblock_inventory(self):
        key = self.wireless_box.get()
        if key == "Misc Accessories":
            return self.wireless_obj_dict[key]
        else:
            # anything with a flux rating should have a wireless_accesories dict list,
            # so make one if it doesn't exist yet
            if "flux" not in self.wireless_obj_dict[key].properties:
                raise AttributeError(f"Object {self.wireless_obj_dict[key].properties['name']} doesn't have a flux "
                                     f"rating!")

            if "wireless_accessories" not in self.wireless_obj_dict[key].properties:
                self.wireless_obj_dict[key].properties["wireless_accessories"] = []

            return self.wireless_obj_dict[key].properties["wireless_accessories"]

    def fill_combobox(self):
        self.wireless_obj_dict = {}
        self.fill_stuff_with_accessories(self.statblock.inventory)
        self.wireless_obj_dict["Misc Accessories"] = self.statblock.misc_wireless_accessories
        self.wireless_box["values"] = list(self.wireless_obj_dict.keys())

        self.wireless_box.set("Misc Accessories")

    def fill_stuff_with_accessories(self, char_list):
        """
        Searches entire character looking for wireless shit.
        :param char_list: Basically the character's inventory, theoretically other things.
        :return: A list of the found things.
        """
        for node in char_list:
            # check for duplicate names
            key = node.name

            # count names that contain the key we want to use
            # we use regex to strip any dupe counts that
            dupe_count = 1
            for k in self.wireless_obj_dict.keys():
                k = re.sub(r"\s*\(\d+\)", "", k)
                if k == key:
                    dupe_count += 1

            # if we have more than one of the thing we want, add the dupe count to the key
            if dupe_count > 1:
                key += " ({})".format(dupe_count)

            if "flux" in node.properties:
                self.wireless_obj_dict[key] = node  # .accessories

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
        selected_item = self.statblock.inventory[self.inv_selected_index]

        # return cash value
        self.statblock.cash += selected_item.properties["cost"]

        self.remove_inv_item(self.inv_selected_index)

    @property
    def recurse_check_func(self):
        def wireless_accessories_recurse_check(val):
            return "cost" not in val.keys()

        return wireless_accessories_recurse_check

    @property
    def recurse_end_func(self):
        def wireless_accessories_recurse_end(key, val, iid):
            val["name"] = key
            self.tree_item_dict[iid] = WirelessAccessory(**val)

        return wireless_accessories_recurse_end

    def on_switch(self):
        self.fill_combobox()
        self.get_accobj(None)

    def load_character(self):
        self.on_switch()
