from abc import ABC
from tkinter import *
from tkinter import ttk

from src import app_data
from src.CharData.accessory import Accessory
from src.CharData.vehicle import Vehicle
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


class VehicleBuyTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent, buy_button_text, sell_button_text):
        super().__init__(parent, buy_button_text, sell_button_text)

    @property
    def library_source(self):
        return self.parent.game_data["Vehicles"]

    @property
    def statblock_inventory(self):
        return self.statblock.vehicles

    @property
    def attributes_to_calculate(self):
        return []

    def buy_callback(self, item):
        if app_data.pay_cash(item.cost):
            self.add_inv_item(item)

    def sell_callback(self, item_index):
        # sell all attached accessories
        vehicle: Vehicle = self.statblock_inventory[item_index]
        accessory: Accessory
        for accessory in vehicle.accessories:
            self.statblock.cash += accessory.cost
        self.statblock.cash += self.statblock_inventory[item_index].cost
        self.remove_inv_item(item_index)

    @property
    def recurse_check_func(self):
        def recurse_check(val):
            return "handling_normal" not in val.keys()

        return recurse_check

    @property
    def recurse_end_func(self):
        def recurse_end_callback(key, val, iid):
            self.tree_item_dict[iid] = Vehicle(name=key, **val)

        return recurse_end_callback

    def on_switch(self):
        pass

    def load_character(self):
        super().load_character()
        self.on_switch()
