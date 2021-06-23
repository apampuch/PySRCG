from abc import ABC
from tkinter import *
from tkinter import ttk

from src import app_data
from src.CharData.accessory import *
from src.CharData.vehicle import Vehicle
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


class VehicleAccessoriesTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent, buy_button_text, sell_button_text):
        super().__init__(parent, buy_button_text, sell_button_text)

        # acc is a vehcile with accessories, so any vehicle really
        # key is name, value is matching thing with it
        self.accobj_dict = {}

        # fill stuff with memory
        self.accessory_things_box = ttk.Combobox(self, values=self.accobj_dict.keys(), state="readonly", width=30)
        self.fill_combobox()

        self.accessory_things_box.bind("<<ComboboxSelected>>", self.get_accobj)

        self.accessory_things_box.grid(column=2, row=1)

    def fill_combobox(self):
        self.accobj_dict = {}
        self.fill_stuff_with_accessories(self.statblock.vehicles)
        self.accobj_dict["Unattached Accessories"] = self.statblock.other_accessories
        self.accessory_things_box["values"] = list(self.accobj_dict.keys())

        self.accessory_things_box.set("Unattached Accessories")

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
            for k in self.accobj_dict.keys():
                k = re.sub(r"\s*\(\d+\)", "", k)
                if k == key:
                    dupe_count += 1

            # if we have more than one of the thing we want, add the dupe count to the key
            if dupe_count > 1:
                key += " ({})".format(dupe_count)

            if hasattr(node, "accessories"):
                self.accobj_dict[key] = node  # .accessories

    def get_accobj(self, event):
        """Fills the inventory box with software from the selected memobj"""
        # clear list box
        self.inventory_list.delete(0, END)

        for obj in self.statblock_inventory:
            self.inventory_list.insert(END, obj.name)

    @property
    def library_source(self):
        return self.parent.game_data["Vehicle Accessories"]

    @property
    def statblock_inventory(self):
        # return self.accobj_dict[self.accessory_things_box.get()]

        # this one is done differently
        # we store the entire vehicle in the dict instead of the inventory unless it's other_accessories
        # so if it's an actual vehicle we need to get the accessories property from it and return that
        key = self.accessory_things_box.get()
        if key == "Unattached Accessories":
            return self.accobj_dict[key]
        else:
            return self.accobj_dict[key].accessories

    @property
    def selected_vehicle(self):
        key = self.accessory_things_box.get()
        if key == "Unattached Accessories":
            return None
        else:
            return self.accobj_dict[key]

    @property
    def attributes_to_calculate(self):
        return ["cost"]

    def buy_callback(self, item):
        enough_cargo = True
        if hasattr(item, "cf_cost"):
            enough_cargo = self.has_cargo(item)

        can_mount = True
        if type(item) == Mount:
            can_mount = self.mount_callback(item)

        if app_data.pay_cash(item.cost, can_mount, enough_cargo):
            self.add_inv_item(item)

    def has_cargo(self, new_item):
        """Checks the accessories on the vehicle, returns true if we can fit the new one, false if we can't."""
        v = self.selected_vehicle

        # return true if not a vehicle, should only be true if it's other_accessories
        if v is None:
            return True

        cargo_total = 0
        for item in self.statblock_inventory:
            if hasattr(item, "cf_cost"):
                cargo_total += item.cf_cost

        return cargo_total + new_item.cf_cost <= v.cargo

    def mount_callback(self, new_mount) -> bool:
        """Checks the mounts already on the vehicle, returns true if we can fit the new mount, false if we can't."""
        v = self.selected_vehicle

        # return true if not a vehicle, should only be true if it's other_accessories
        if v is None:
            return True

        mount_total = 0
        for item in self.statblock_inventory:
            if type(item) == Mount:
                mount_total += item.body_cost

        return mount_total + new_mount.body_cost <= v.body

    def sell_callback(self, item_index):
        self.statblock.cash += self.statblock_inventory[item_index].cost
        self.remove_inv_item(item_index)

    @property
    def recurse_check_func(self):
        def recurse_check(val):
            return "cost" not in val.keys()

        return recurse_check

    @property
    def recurse_end_func(self):
        def recurse_end_callback(key, val, iid):
            try:
                if "recoil_compensation" in val.keys():
                    self.tree_item_dict[iid] = Mount(name=key, **val)
                elif "damage" in val.keys():
                    self.tree_item_dict[iid] = VehicleWeapon(name=key, **val)
                else:
                    self.tree_item_dict[iid] = Accessory(name=key, **val)
            except TypeError as e:
                print("Error with {}:".format(key))
                print(e)
                print()

        return recurse_end_callback

    def on_switch(self):
        self.fill_combobox()
        self.get_accobj(None)

    def load_character(self):
        self.on_switch()
