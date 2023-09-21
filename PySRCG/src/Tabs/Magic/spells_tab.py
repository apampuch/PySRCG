from abc import ABC
from copy import copy

from src import app_data
from src.CharData.spell import Spell
from src.GenModes.finalized import Finalized
from src.GenModes.priority import Priority
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.adjustment import Adjustment

from tkinter import *


class SpellsTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "SpellsTab", buy_button_text="Learn", sell_button_text="Unlearn", plus_and_minus=True)

        self.buy_spell_point_button = Button(self, text="Buy Spell Point", command=self.buy_spell_point_callback)
        self.sell_spell_point_button = Button(self, text="Sell Spell Point", command=self.sell_spell_point_callback)

    @property
    def recurse_check_func(self):
        def spell_tab_recurse_check(val):
            return "drain" not in val.keys()

        return spell_tab_recurse_check

    @property
    def recurse_end_func(self):
        def spell_tab_recurse_end_callback(key, val, iid):
            # key is a string
            # val is a _dict from a json
            val["name"] = key
            self.tree_item_dict[iid] = Spell(**val, force=0)

        return spell_tab_recurse_end_callback

    @property
    def library_source(self):
        try:
            return app_data.game_data["Spells"]
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.spells

    def buy_callback(self, selected):
        magic_total = 0

        # check to make sure it's not already there
        for val in self.statblock.spells:
            if val.properties["name"] == self.library_selected.properties["name"]:
                print("Already have that learned!")
                return

            magic_total += val.properties["force"]

        if self.statblock.gen_mode.point_purchase_allowed(magic_total, "magic"):
            # make a spell object, then add to the player's magic list

            new_spell = copy(self.library_selected)
            new_spell.properties["force"] += 1
            self.add_inv_item(new_spell)

            # do this if we're finalized
            if type(self.gen_mode) == Finalized:
                def undo():
                    return  # do nothing, will be handled in unlearn_spell

                adjustment = Adjustment(1, "add_spell_" + new_spell.properties["name"], undo, "Add new spell")
                self.gen_mode.add_adjustment(adjustment)

            self.calculate_total()

    def sell_callback(self, selected_index):
        selected_spell: Spell = self.statblock.spells[self.inv_selected_index]

        if type(self.gen_mode) == Finalized:
            if self.gen_mode.remove_by_adjustment_type(selected_spell, "add_spell_", "increase_spell_"):
                self.gen_mode.undo("add_spell_" + selected_spell.properties["name"])
                self.remove_inv_item(self.inv_selected_index)
            else:
                print("Can't remove that!")

        else:
            self.remove_inv_item(self.inv_selected_index)
        self.calculate_total()

    def plus_callback(self):
        # set the check value based on the generation mode
        check_val = 1 if type(self.gen_mode) == Finalized else self.get_total()

        if self.list_selected is not None and \
                self.statblock.gen_mode.point_purchase_allowed(check_val, "magic"):
            selected_spell = self.statblock.spells[self.inv_selected_index]
            max_force = 99 if type(self.gen_mode) == Finalized else 6

            if selected_spell.properties["force"] < max_force:
                selected_spell.properties["force"] += 1

                # update UI by removing the old one and inserting a new one at the same index
                i = self.inv_selected_index
                self.inventory_list.delete(i)
                self.inventory_list.insert(i, selected_spell.force_and_name())
                self.inventory_list.selection_set(i)

                if type(self.gen_mode) == Finalized:
                    # undo function
                    def undo():
                        selected_spell.properties["force"] -= 1

                    adjustment = Adjustment(1, "increase_spell_" + selected_spell.properties["name"], undo)
                    self.gen_mode.add_adjustment(adjustment)

                self.calculate_total()

    def minus_callback(self):
        if self.list_selected is not None:
            selected_spell = self.statblock.spells[self.inv_selected_index]

            if selected_spell.properties["force"] > 1:
                if type(self.gen_mode) is Finalized:
                    undo_type = "increase_spell_" + selected_spell.properties["name"]
                    self.statblock.gen_mode.undo(undo_type)
                else:
                    selected_spell.properties["force"] -= 1

                # update UI by removing the old one and inserting a new one at the same index
                i = self.inv_selected_index
                self.inventory_list.delete(i)
                self.inventory_list.insert(i, selected_spell.force_and_name())
                self.inventory_list.selection_set(i)

                self.calculate_total()

    def buy_spell_point_callback(self):
        if type(self.statblock.gen_mode) is not Finalized:
            if self.statblock.pay_cash(25000):
                if type(self.statblock.gen_mode) is Priority:
                    # increment purchased and max by 1
                    self.statblock.gen_mode.increment_purchased_magic_points()
                    self.calculate_total()
                else:
                    self.statblock.add_cash(25000)  # undo paid cash
                    raise NotImplementedError("Current gen mode not implemented for this")
            else:
                print("Not enough cash!")
        else:
            print("Need to not be finalized to use this!")

    def sell_spell_point_callback(self):
        if type(self.statblock.gen_mode) is not Finalized:
            if type(self.statblock.gen_mode) is Priority:
                if self.statblock.gen_mode.decrement_purchased_magic_points():
                    self.statblock.add_cash(25000)
                    self.calculate_total()
                else:
                    print("No more spell points to sell!")
            else:
                raise NotImplementedError("Current gen mode not implemented for this")
        else:
            print("Need to not be finalized to use this!")

    def get_total(self):
        total = 0

        for spell in self.statblock.spells:
            total += spell.properties["force"]

        for focus in self.statblock.foci:
            if focus.properties["bound"]:
                total += focus.properties["karma_cost"]

        return total

    def calculate_total(self):
        """Totals all spell points and updates the top karma bar."""
        self.statblock.gen_mode.update_total(self.get_total(), "magic")

    def on_tradition_change(self):
        return

    def update_karma_bar(self):
        vals = self.gen_mode.karma_bar_vals["spells"]
        app_data.top_bar.karma_bar.configure(variable=vals[0], maximum=vals[1].get())

    def load_character(self):
        # clear everything
        self.inventory_list.delete(0, END)

        # add stuff to the list
        for spell in self.statblock.spells:
            self.inventory_list.insert(END, spell.force_and_name())

        self.on_switch()

    def on_switch(self):
        # show or hide spell point buttons based on finalized status
        if type(self.gen_mode) is not Finalized:
            self.buy_spell_point_button.grid(column=3, row=1)
            self.sell_spell_point_button.grid(column=4, row=1)
        else:
            self.buy_spell_point_button.grid_forget()
            self.sell_spell_point_button.grid_forget()

        self.calculate_total()
