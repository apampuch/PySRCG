import re
from abc import ABC
from tkinter import ttk, END

from src.CharData.wireless_accesory import WirelessAccessory
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.app_data import pay_cash


class WirelessTab(ThreeColumnBuyTab):
    def __init__(self, parent):
        super().__init__(parent)

        self.wireless_obj_dict = {}
        self.wireless_box = ttk.Combobox(self, values=self.wireless_obj_dict.keys(), state="readonly")
        # self.fill_combobox()

        self.wireless_box.bind("<<ComboboxSelected>>", self.get_accobj)

        self.wireless_box.grid(column=3, row=1)

    @property
    def library_source(self):
        try:
            return self.parent.game_data["Wireless Accessories"]
        except KeyError:
            return {}

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
        self.fill_stuff_with_accessories(self.statblock.cyberware)

        # get drones
        drones = []
        drone_names = []
        for vehicle in self.statblock.vehicles:
            for accessory in vehicle.properties["vehicle_accessories"]:
                if accessory.name == 'Remote Control Gear':
                    drones.append(accessory)

                    custom_name = vehicle.properties["name"]
                    drone_names.append(custom_name)

        self.fill_stuff_with_accessories(drones, drone_names)

        self.wireless_obj_dict["Misc Accessories"] = self.statblock.misc_wireless_accessories
        self.wireless_box["values"] = list(self.wireless_obj_dict.keys())

        self.wireless_box.set("Misc Accessories")

    def fill_stuff_with_accessories(self, char_list, custom_names=None):
        """
        Searches entire character looking for wireless shit.
        :param char_list: An inventory of gear or other things that can have a flux rating.
        :param custom_names: A list of custom names to use, should be the same length as char_list. Any None entry will use the regular name.
        :return: A list of the found things.
        """
        for i in range(0, len(char_list)):

            node = char_list[i]
            if "flux" in node.properties:
                # use a custom name unless custom_names is None
                # if it isn't None but an entry is None, use normal name
                if custom_names is None:
                    key = node.name
                elif custom_names[i] is None:
                    key = node.name
                else:
                    key = custom_names[i]

                # check for duplicate names
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
        selected_item = self.statblock_inventory[self.inv_selected_index]

        # return cash value
        self.statblock.add_cash(selected_item.properties["cost"])

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
