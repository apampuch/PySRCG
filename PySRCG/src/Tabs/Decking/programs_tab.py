from src.CharData.program import Program
from tkinter import *
from tkinter import ttk
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab

import src.app_data as app_data


class ProgramsTab(ThreeColumnBuyTab):
    def __init__(self, parent,
                 buy_button_text,
                 sell_button_text):

        super().__init__(parent, buy_button_text, sell_button_text)

        # memobj is anything with in-game memory
        # key is name, value is matching thing with it
        self.memobj_dict = {}

        # fill stuff with memory
        self.memory_things_box = ttk.Combobox(self, values=self.memobj_dict.keys(), state="readonly")
        self.fill_combobox()

        self.memory_things_box.bind("<<ComboboxSelected>>", self.get_memobj_memory)

        self.memory_things_box.grid(column=3, row=1)

    def fill_combobox(self):
        self.memobj_dict = {}
        self.fill_stuff_with_memory(self.statblock.inventory)
        self.fill_stuff_with_memory(self.statblock.cyberware)
        self.fill_stuff_with_memory(self.statblock.decks)
        self.memobj_dict["Misc Software"] = self.statblock.other_programs
        self.memory_things_box["values"] = list(self.memobj_dict.keys())

        self.memory_things_box.set("Misc Software")

    def fill_stuff_with_memory(self, char_list):
        """Traverses entire character looking for stuff with stored_memory.
        :param char_list: something in self.statblock that could have something with memory, like inventory or cyberware
        :type char_list: list
        """
        for node in char_list:
            # check for duplicate names
            key = node.name

            # count names that contain the key we want to use
            # we use regex to strip any dupe counts that
            dupe_count = 1
            for k in self.memobj_dict.keys():
                k = re.sub(r"\s*\(\d+\)", "", k)
                if k == key:
                    dupe_count += 1

            # if we have more than one of the thing we want, add the dupe count to the key
            if dupe_count > 1:
                key += " ({})".format(dupe_count)

            if "stored_memory" in node.properties:
                self.memobj_dict[key] = node.properties["stored_memory"]

    def get_memobj_memory(self, event):
        """Fills the inventory box with software from the selected memobj"""
        # clear list box
        self.inventory_list.delete(0, END)

        for soft in self.statblock_inventory:
            self.inventory_list.insert(END, self.name_for_list(soft))

    @property
    def library_source(self):
        return self.parent.game_data["Programs"]

    @property
    def statblock_inventory(self):
        """This one should return the currently selected thing we're storing programs on."""
        return self.memobj_dict[self.memory_things_box.get()]

    @staticmethod
    def name_for_list(x):
        return "{}: Rating {}".format(x.properties["name"], x.properties["rating"])

    def buy_callback(self, item):
        if app_data.pay_cash(item.properties["cost"]):
            self.add_inv_item(item)

    def sell_callback(self, item_index):
        self.statblock.cash += self.statblock_inventory[item_index].properties["cost"]
        self.remove_inv_item(item_index)

    @property
    def recurse_check_func(self):
        def recurse_check(val):
            return "multiplier" not in val.keys()

        return recurse_check

    @property
    def recurse_end_func(self):
        def recurse_end_callback(key, val, iid):
            self.tree_item_dict[iid] = Program(name=key, **val)

        return recurse_end_callback

    def on_switch(self):
        self.fill_combobox()
        self.get_memobj_memory(None)

    def load_character(self):
        self.on_switch()
