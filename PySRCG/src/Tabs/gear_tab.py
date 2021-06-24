from src.app_data import pay_cash
from src.Tabs.notebook_tab import NotebookTab
from src.utils import recursive_treeview_fill, treeview_get, get_variables, calculate_attributes
from tkinter import *
from tkinter import ttk
from src.CharData.gear import *

ATTRIBUTES_TO_CALCULATE = ["cost", "weight", "availability_rating", "availability_time", "street_index", "rating",
                           "transaction_limit"]  # find a better way to do this, maybe per-item?


class GearTab(NotebookTab):
    @property
    def tree_selected_item(self):
        return treeview_get(self.gear_library, self.tree_item_dict)

    @property
    def inv_selected_item(self):
        """ID of the index of the selected item"""
        selection = self.inventory_list.curselection()
        if len(selection) is 0:
            return None
        return selection[-1]

    def __init__(self, parent):
        super().__init__(parent)

        # used to validate input
        self.vcmd = (self.register(self.int_validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.tree_item_dict = {}  # maps terminal children iids to items

        # frame to hold the list
        self.gear_library = ttk.Treeview(self, height=20, show="tree")
        self.gear_library_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.gear_library.yview)

        # description box
        self.desc_box = Text(self, width=40, state=DISABLED, bg='#d1d1d1')
        self.desc_box_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.desc_box.yview)

        # inventory list
        self.inventory_list = Listbox(self, width=40)
        self.inventory_list_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.inventory_list.yview)

        # buy button
        self.buy_button = Button(self, text="Buy", command=self.on_buy_click)

        # sell button
        self.sell_button = Button(self, text="Sell", command=self.on_sell_click)

        def gear_tab_recurse_check(val):
            return "cost" not in val.keys()

        def gear_tab_recurse_end_callback(key, val, iid):
            self.tree_item_dict[iid] = find_gear_by_dict(key, val)

        # fill the treeview with items
        recursive_treeview_fill(self.parent.game_data["Items"], "", self.gear_library,
                                gear_tab_recurse_check, gear_tab_recurse_end_callback)

        # variable objects frame and list
        self.variables_frame = Frame(self)
        self.variables_dict = {}

        # bind events and shit
        self.gear_library.bind("<<TreeviewSelect>>", self.on_tree_item_click)
        self.gear_library["yscrollcommand"] = self.gear_library_scroll.set
        self.inventory_list.bind("<<ListboxSelect>>", self.on_inv_item_click)
        self.desc_box["yscrollcommand"] = self.desc_box_scroll.set
        self.inventory_list["yscrollcommand"] = self.inventory_list_scroll.set

        # grids
        self.gear_library.grid(column=0, row=0, sticky=(N, S))
        self.gear_library_scroll.grid(column=1, row=0, sticky=(N, S))
        self.desc_box.grid(column=2, row=0, sticky=(N, S))
        self.desc_box_scroll.grid(column=3, row=0, sticky=(N, S))
        self.inventory_list.grid(column=4, row=0, sticky=(N, S))
        self.inventory_list_scroll.grid(column=5, row=0, sticky=(N, S))

        self.buy_button.grid(column=0, row=1, sticky=N)
        self.sell_button.grid(column=4, row=1, sticky=N)

        self.variables_frame.grid(column=0, row=2)

    def add_inventory_item(self, item: Gear):
        self.statblock.inventory.append(item)
        self.inventory_list.insert(END, item.name)

    def remove_inventory_item(self, index):
        del self.statblock.inventory[index]
        self.inventory_list.delete(index)

    def fill_description_box(self, contents):
        """Clears the item description box and fills it with contents."""
        # temporarily unlock box, clear it, set the text, then re-lock it
        self.desc_box.config(state=NORMAL)
        self.desc_box.delete(1.0, END)
        self.desc_box.insert(END, contents)
        self.desc_box.config(state=DISABLED)

    def on_tree_item_click(self, event):
        # only select the last one selected if we've selected multiple things
        selected = self.gear_library.selection()[-1]

        if selected in self.tree_item_dict.keys():
            selected_item = self.tree_item_dict[selected]
            # destroy all variable objects
            self.variables_dict = {}
            for child in self.variables_frame.winfo_children():
                child.destroy()

            # get any variables in the item
            self.variables_dict = get_variables(selected_item, ATTRIBUTES_TO_CALCULATE)

            self.fill_description_box(selected_item.report())

        # make variable objects if any
        i = 0
        for var in self.variables_dict.keys():
            var_frame = Frame(self.variables_frame)
            Label(var_frame, text="{}:".format(var)).grid(column=0, row=0)  # label
            Entry(var_frame, textvariable=self.variables_dict[var], validate="key", validatecommand=self.vcmd) \
                .grid(column=1, row=0)
            var_frame.grid(column=0, row=i)
            i += 1

    def on_inv_item_click(self, event):
        item_report = self.statblock.inventory[self.inventory_list.curselection()[-1]].report()
        self.fill_description_box(item_report)

    def on_buy_click(self):
        # make copy of the item from the dict
        item = treeview_get(self.gear_library, self.tree_item_dict)
        if item is not None:
            # make a new dict from the variables dict that we can pass into parse_arithmetic()
            # because parse_arithmetic() can't take IntVars
            var_dict = {}
            for key in self.variables_dict.keys():
                var_dict[key] = self.variables_dict[key].get()

            # calculate any arithmetic expressions we have
            calculate_attributes(item, var_dict, ATTRIBUTES_TO_CALCULATE)

            if pay_cash(item.cost):
                self.add_inventory_item(item)
            else:
                print("Not paid!")
        else:
            print("Can't buy that!")

    def on_sell_click(self):
        # don't do anything if nothing is selected
        if len(self.inventory_list.curselection()) is 0:
            return
        selected_item = self.statblock.inventory[self.inv_selected_item]

        # return cash value
        self.statblock.cash += selected_item.cost

        self.remove_inventory_item(self.inv_selected_item)

    def int_validate(self, action, index, value_if_allowed,
                     prior_value, text, validation_type, trigger_type, widget_name):
        """
        Validates if entered text can be an int and over 0.
        :param action:
        :param index:
        :param value_if_allowed:
        :param prior_value:
        :param text:
        :param validation_type:
        :param trigger_type:
        :param widget_name:
        :return: True if text is valid
        """
        if value_if_allowed == "":
            return True

        if value_if_allowed:
            try:
                i = int(value_if_allowed)
                if i > 0:
                    return True
                else:
                    self.bell()
                    return False
            except ValueError:
                self.bell()
                return False
        else:
            self.bell()
            return False

    def on_switch(self):
        pass

    def load_character(self):
        self.inventory_list.delete(0, END)
        for item in self.statblock.inventory:
            self.inventory_list.insert(END, item.name)
