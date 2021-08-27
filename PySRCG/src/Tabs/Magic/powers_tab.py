from abc import ABC
from copy import copy

from src import app_data
from src.CharData.power import Power
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.utils import treeview_get, recursive_treeview_fill

from tkinter import *
from tkinter import ttk


class PowersTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)

        self.plus_button = Button(self, text="+", command=self.on_plus_click)
        self.minus_button = Button(self, text="-", command=self.on_minus_click)

        self.plus_button.grid(column=2, row=1, sticky=W)
        self.minus_button.grid(column=3, row=1, sticky=W)

    @property
    def library_source(self):
        return self.parent.game_data["Powers"]

    @property
    def statblock_inventory(self):
        return self.statblock.powers

    @property
    def recurse_check_func(self):
        def power_recurse_check(val):
            return "cost" not in val.keys()

        return power_recurse_check

    @property
    def recurse_end_func(self):
        def power_recurse_end(key, val, iid):
            val["name"] = key
            self.tree_item_dict[iid] = Power(**val)

        return power_recurse_end

    @property
    def attributes_to_calculate(self):
        return []

    def buy_callback(self, selected):
        # check to make sure the power is not already there
        # TODO make this allow the same power with different aspects, like the extra skill dice power
        for power in self.statblock.powers:
            if power.name == self.library_selected.name:
                print("Already known!")
                return

        total_power_points = self.statblock.power_points

        # print("Library Selected: " + self.library_selected.name)
        # power = copy(self.library_selected)

        # make sure we have enough power points remaining
        if total_power_points + selected.properties["cost"] * selected.properties["level"] <= \
                self.statblock.total_power_points:
            self.add_inv_item(selected, lambda x: f"{x.properties['name']} level {x.properties['level']}: {x.properties['cost']}")
            # fix internal variable shit
            self.calculate_total()

        else:
            print("Not enough magic remaining!")

    def sell_callback(self, selected_index):
        self.remove_inv_item(selected_index)

    def on_plus_click(self):
        if self.list_selected is None:
            return

        base_cost = self.list_selected.properties["cost"] / self.list_selected.properties["level"]

        # TODO if max_levels == null pretend max_levels == magic attribute

        # TODO check if we're under max_levels

        if self.statblock.power_points + base_cost <= self.statblock.magic:
            self.list_selected.properties["cost"] += base_cost
            self.list_selected.properties["level"] += 1

            self.update_inventory_text_at_index(self.inv_selected_index,
                                                f"{self.list_selected.properties['name']} level "
                                                f"{self.list_selected.properties['level']}: "
                                                f"{self.list_selected.properties['cost']}")

            self.calculate_total()

        else:
            print("Not enough magic remaining!")

    def on_minus_click(self):
        if self.list_selected is None:
            return

        base_cost = self.list_selected.properties["cost"] / self.list_selected.properties["level"]

        if self.list_selected.properties["level"] > 1:
            self.list_selected.properties["cost"] -= base_cost
            self.list_selected.properties["level"] -= 1

            self.update_inventory_text_at_index(self.inv_selected_index,
                                                f"{self.list_selected.properties['name']} level "
                                                f"{self.list_selected.properties['level']}: "
                                                f"{self.list_selected.properties['cost']}")

            self.calculate_total()

    def on_switch(self):
        self.calculate_total()

    def calculate_total(self):
        # unlike the other tabs places we directly manipulate the top bar
        # since this has nothing to do with the generation mode
        self.statblock.power_points_ui_var.set(self.statblock.power_points)
        app_data.top_bar.update_karma_bar("{:.2f}".format(self.statblock.power_points),
                                          self.statblock.total_power_points, "Powers Tab")

    def load_character(self):
        super().load_character()
        self.calculate_total()
