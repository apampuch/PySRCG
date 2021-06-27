from tkinter import *
from tkinter import ttk

from copy import copy
from src.Tabs.notebook_tab import NotebookTab
from src.utils import recursive_treeview_fill, treeview_get, get_variables, calculate_attributes

from abc import ABC, abstractmethod


class ThreeColumnBuyTab(NotebookTab, ABC):
    """
    This is a generic class for a tab that has three columns:
    A treeview to display a library of things to buy.
    A description box to show info for the selected item
    A list for all bought items
    """
    @property
    def library_selected(self):  # returns a deck OR a program
        return treeview_get(self.object_library, self.tree_item_dict, self.treeview_get_make_copy)

    @property
    def inv_selected_item(self):
        """ID of the index of the selected item"""
        selection = self.inventory_list.curselection()
        if len(selection) is 0:
            return None
        return selection[-1]

    def __init__(self, parent,
                 buy_button_text="Buy",
                 sell_button_text="Sell",
                 treeview_get_make_copy=True):
        super().__init__(parent)
        self.treeview_get_make_copy = treeview_get_make_copy

        # used to validate input
        self.vcmd = (self.register(self.int_validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.tree_item_dict = {}  # maps terminal children iids to items

        # frame to hold the list
        self.object_library = ttk.Treeview(self, height=20, show="tree")
        self.object_library_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.object_library.yview)

        # description box
        self.desc_box = Text(self, width=40, state=DISABLED, bg='#d1d1d1')
        self.desc_box_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.desc_box.yview)

        # inventory list
        self.inventory_list = Listbox(self, width=40)
        self.inventory_list_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.inventory_list.yview)

        # buy button
        self.buy_button = Button(self, text=buy_button_text, command=self.on_buy_click)

        # sell button
        self.sell_button = Button(self, text=sell_button_text, command=self.on_sell_click)

        # variable objects frame and list, things like rating usually
        self.variables_frame = Frame(self)
        self.variables_dict = {}

        # bind events and shit
        self.object_library.bind("<<TreeviewSelect>>", self.on_tree_item_click)
        self.object_library["yscrollcommand"] = self.object_library_scroll.set
        self.inventory_list.bind("<<ListboxSelect>>", self.on_inv_item_click)
        self.desc_box["yscrollcommand"] = self.desc_box_scroll.set
        self.inventory_list["yscrollcommand"] = self.inventory_list_scroll.set

        # fill the treeview with items
        recursive_treeview_fill(self.library_source, "", self.object_library,
                                self.recurse_check_func, self.recurse_end_func)

        # grids
        self.object_library.grid(column=0, row=0, sticky=(N, S))
        self.object_library_scroll.grid(column=1, row=0, sticky=(N, S))
        self.desc_box.grid(column=2, row=0, sticky=(N, S))
        self.desc_box_scroll.grid(column=3, row=0, sticky=(N, S))
        self.inventory_list.grid(column=4, row=0, sticky=(N, S))
        self.inventory_list_scroll.grid(column=5, row=0, sticky=(N, S))

        self.buy_button.grid(column=0, row=1, sticky=N)
        self.sell_button.grid(column=4, row=1, sticky=N)

        self.variables_frame.grid(column=0, row=2)

    @property
    @abstractmethod
    def library_source(self):
        """The thing that the library needs to be filled from."""
        pass

    @property
    @abstractmethod
    def statblock_inventory(self):
        pass

    @property
    @abstractmethod
    def attributes_to_calculate(self):
        """List of variables to look for."""
        pass

    @abstractmethod
    def buy_callback(self, selected):
        """Called on clicking a buy button. All variable calculations should have been performed."""
        pass

    @abstractmethod
    def sell_callback(self, selected_index):
        pass

    @property
    @abstractmethod
    def recurse_check_func(self):
        """Returns a function that returns true if you want to keep recursing through a tree."""
        pass

    @property
    @abstractmethod
    def recurse_end_func(self):
        """Needs to return a function like this:
         def recurse_end_callback(key, val, iid):
            # self.tree_item_dict[iid] = SOMETHING(name=key, **val)"""
        pass

    def fill_description_box(self, contents):
        """Clears the item description box and fills it with contents."""
        # temporarily unlock box, clear it, set the text, then re-lock it
        self.desc_box.config(state=NORMAL)
        self.desc_box.delete(1.0, END)
        self.desc_box.insert(END, contents)
        self.desc_box.config(state=DISABLED)

    def add_inv_item(self, item, listbox_string=lambda x: x.name):
        """Adds item to the inventory this tab is linked to."""
        self.statblock_inventory.append(item)
        self.inventory_list.insert(END, listbox_string(item))

    def remove_inv_item(self, index):
        """Removes an item at index from the inventory this tab is linked to."""
        del self.statblock_inventory[index]
        self.inventory_list.delete(index)

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

    def on_inv_item_click(self, event):
        # for some reason this gets called when you swap the combobox with something selected on ProgramsTab
        # this shit exists just so we don't throw an error
        if len(self.inventory_list.curselection()) == 0:
            self.fill_description_box("")
            return

        item_report = self.statblock_inventory[self.inventory_list.curselection()[-1]].report()
        self.fill_description_box(item_report)

    def on_buy_click(self):
        # make copy of the item from the dict
        if self.library_selected is not None:

            # make copy of item and calculate variables we input
            # TODO try baleeting this
            item = copy(self.library_selected)
            var_dict = {}
            for key in self.variables_dict.keys():
                var_dict[key] = self.variables_dict[key].get()

            # calculate any arithmetic expressions we have
            calculate_attributes(item, var_dict, self.attributes_to_calculate)

            self.buy_callback(item)
        else:
            print("Can't buy that!")

    def on_sell_click(self):
        # don't do anything if nothing is selected
        if len(self.inventory_list.curselection()) > 0:
            self.sell_callback(self.inv_selected_item)

    def on_tree_item_click(self, event):
        # only select the last one selected if we've selected multiple things
        selected = self.object_library.selection()[-1]

        if selected in self.tree_item_dict.keys():
            selected_item = self.tree_item_dict[selected]
            # destroy all variable objects
            self.variables_dict = {}
            for child in self.variables_frame.winfo_children():
                child.destroy()

            # get any variables in the item
            self.variables_dict = get_variables(selected_item, self.attributes_to_calculate)

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

    @abstractmethod
    def on_switch(self):
        pass

    @abstractmethod
    def load_character(self):
        self.inventory_list.delete(0, END)
        for item in self.statblock_inventory:
            self.inventory_list.insert(END, item.name)