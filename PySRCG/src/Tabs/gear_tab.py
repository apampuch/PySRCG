from abc import ABC

from src.app_data import pay_cash
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab
from src.CharData.gear import *

ATTRIBUTES_TO_CALCULATE = ["cost", "weight", "availability_rating", "availability_time", "street_index", "rating",
                           "transaction_limit"]  # find a better way to do this, maybe per-item?


class GearTab(ThreeColumnBuyTab, ABC):
    @property
    def inv_selected_item(self):
        """ID of the index of the selected item"""
        selection = self.inventory_list.curselection()
        if len(selection) is 0:
            return None
        return selection[-1]

    def __init__(self, parent, buy_button_text, sell_button_text):
        super().__init__(parent)

    @property
    def recurse_check_func(self):
        def gear_tab_recurse_check(val):
            return "cost" not in val.keys()

        return gear_tab_recurse_check

    @property
    def recurse_end_func(self):
        def gear_tab_recurse_end_callback(key, val, iid):
            self.tree_item_dict[iid] = find_gear_by_dict(key, val)

        return gear_tab_recurse_end_callback

    def buy_callback(self, selected):
        if pay_cash(selected.cost):
            self.add_inv_item(selected)
        else:
            print("Not enough money!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock.inventory[self.inv_selected_item]

        # return cash value
        self.statblock.cash += selected_item.cost

        self.remove_inv_item(self.inv_selected_item)

    @property
    def attributes_to_calculate(self):
        return ["cost", "weight", "availability_rating", "availability_time",
                "street_index", "rating", "transaction_limit"]

    @property
    def library_source(self):
        return self.parent.game_data["Items"]

    @property
    def statblock_inventory(self):
        return self.statblock.inventory

    # def add_inventory_item(self, item: Gear):
    #     self.statblock.inventory.append(item)
    #     self.inventory_list.insert(END, item.name)

    # def remove_inventory_item(self, index):
    #     del self.statblock.inventory[index]
    #     self.inventory_list.delete(index)

    # def fill_description_box(self, contents):
    #     """Clears the item description box and fills it with contents."""
    #     # temporarily unlock box, clear it, set the text, then re-lock it
    #     self.desc_box.config(state=NORMAL)
    #     self.desc_box.delete(1.0, END)
    #     self.desc_box.insert(END, contents)
    #     self.desc_box.config(state=DISABLED)

    # def on_tree_item_click(self, event):
    #     # only select the last one selected if we've selected multiple things
    #     selected = self.gear_library.selection()[-1]
    #
    #     if selected in self.tree_item_dict.keys():
    #         selected_item = self.tree_item_dict[selected]
    #         # destroy all variable objects
    #         self.variables_dict = {}
    #         for child in self.variables_frame.winfo_children():
    #             child.destroy()
    #
    #         # get any variables in the item
    #         self.variables_dict = get_variables(selected_item, ATTRIBUTES_TO_CALCULATE)
    #
    #         self.fill_description_box(selected_item.report())
    #
    #     # make variable objects if any
    #     i = 0
    #     for var in self.variables_dict.keys():
    #         var_frame = Frame(self.variables_frame)
    #         Label(var_frame, text="{}:".format(var)).grid(column=0, row=0)  # label
    #         Entry(var_frame, textvariable=self.variables_dict[var], validate="key", validatecommand=self.vcmd) \
    #             .grid(column=1, row=0)
    #         var_frame.grid(column=0, row=i)
    #         i += 1

    # def on_inv_item_click(self, event):
    #     item_report = self.statblock.inventory[self.inventory_list.curselection()[-1]].report()
    #     self.fill_description_box(item_report)

    # def on_buy_click(self):
    #     # make copy of the item from the dict
    #     item = treeview_get(self.gear_library, self.tree_item_dict)
    #     if item is not None:
    #         # make a new dict from the variables dict that we can pass into parse_arithmetic()
    #         # because parse_arithmetic() can't take IntVars
    #         var_dict = {}
    #         for key in self.variables_dict.keys():
    #             var_dict[key] = self.variables_dict[key].get()
    #
    #         # calculate any arithmetic expressions we have
    #         calculate_attributes(item, var_dict, ATTRIBUTES_TO_CALCULATE)
    #
    #         if pay_cash(item.cost):
    #             self.add_inventory_item(item)
    #         else:
    #             print("Not enough money!")
    #     else:
    #         print("Can't buy that!")

    # def on_sell_click(self):
    #     # don't do anything if nothing is selected
    #     if len(self.inventory_list.curselection()) is 0:
    #         return
    #     selected_item = self.statblock.inventory[self.inv_selected_item]
    #
    #     # return cash value
    #     self.statblock.cash += selected_item.cost
    #
    #     self.remove_inventory_item(self.inv_selected_item)

    def on_switch(self):
        pass

    def load_character(self):
        super().load_character()
        self.on_switch()
