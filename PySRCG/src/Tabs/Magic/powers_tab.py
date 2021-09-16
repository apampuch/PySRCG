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
        super().__init__(parent, buy_button_text="Learn", sell_button_text="Unlearn", plus_and_minus=True)

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

    @staticmethod
    def name_for_list(x):
        ret = f"{x.properties['name']} "
        if "options" in x.properties:
            for option in x.properties["options"].values():
                ret += f"({option}) "

        ret += f"level {x.properties['level']}: {x.properties['cost']}"
        return ret

    def power_already_known(self, new_power):
        # a big fuckin' messy logic tree because fuck doing it the leetcode way
        for old_power in self.statblock.powers:
            if old_power.name == new_power.name:
                if "options" in old_power.properties:
                    # already known if properties match exactly
                    # don't check if the option keys are different, they should always be the same for stuff with the
                    # same name
                    for option in old_power.properties["options"]:
                        try:
                            # if they don't match, we don't know the power
                            if old_power.properties["options"][option] != new_power.properties["options"][option]:
                                return False
                        except KeyError:
                            print("WARNING: they don't match")
                            return False
                    # if this for loop doesn't trigger, the powers are the same
                    return True

                else:
                    # already known if we have something with the same name and no options
                    return True

        # if nothing else triggers, then we don't know the power
        return False

    def buy_callback(self, selected):
        # check to make sure the power is not already there
        if self.power_already_known(selected):
            print("Already known!")
            return

        total_power_points = self.statblock.power_points

        # print("Library Selected: " + self.library_selected.name)
        # power = copy(self.library_selected)

        # make sure we have enough power points remaining
        if total_power_points + selected.properties["cost"] * selected.properties["level"] <= \
                self.statblock.total_power_points:

            self.add_inv_item(selected)
            # fix internal variable shit
            self.calculate_total()

        else:
            print("Not enough magic remaining!")

    def sell_callback(self, selected_index):
        self.remove_inv_item(selected_index)

    def plus_callback(self):
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

    def minus_callback(self):
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


if __name__ == "__main__":
    class EqNormal:
        def __init__(self, x):
            self.x = x

    class EqAlways:
        def __init__(self, x):
            self.x = x

        def __eq__(self, other):
            return True

    class EqX:
        def __init__(self, x):
            self.x = x

        def __eq__(self, other):
            return self.x == other.x

    fooNorm = EqNormal(2)
    barNorm = EqNormal(2)
    print(f"fooNorm == barNorm: {fooNorm == barNorm}")

    fooAlways = EqAlways(2)
    barAlways = EqAlways(2)
    print(f"fooAlways == barAlways: {fooAlways == barAlways}")

    fooX = EqX(2)
    barX = EqX(2)
    print(f"fooX == barX: {fooX == barX}")
