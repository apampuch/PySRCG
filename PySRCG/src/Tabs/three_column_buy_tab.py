from copy import copy

from tkinter import *
from tkinter import ttk

from typing import List, Callable

from src.Tabs.notebook_tab import NotebookTab
from src.utils import recursive_treeview_fill, treeview_get, get_variables, calculate_attributes

from abc import ABC, abstractmethod


def print_name_and_options(x):
    ret = f"{x.properties['name']} "
    if "options" in x.properties:
        for option in x.properties["options"].values():
            ret += f"({option}) "

    return ret.rstrip()


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
    def list_selected(self):
        return self.statblock_inventory[self.inv_selected_index]

    """
    The reason sell uses index (this) and buy uses the item itself is because listboxes are based on index.
    """
    @property
    def inv_selected_index(self):
        """ID of the index of the selected item"""
        selection = self.inventory_list.curselection()
        if len(selection) is 0:
            return None
        return selection[-1]

    def __init__(self, parent,
                 buy_button_text="Buy",
                 sell_button_text="Sell",
                 add_inv_callbacks: List[Callable] = None,      # callback functions when adding to inventory
                 remove_inv_callbacks: List[Callable] = None,   # callback functions when removing from inventory
                 treeview_get_make_copy=True,
                 show_quantity=False,
                 show_race_mods=False,
                 buy_from_list=False,
                 plus_and_minus=False):  # allow buying the selected object from the inventory list

        if add_inv_callbacks is None:
            add_inv_callbacks = []

        if remove_inv_callbacks is None:
            remove_inv_callbacks = []

        super().__init__(parent)
        self.add_inv_callbacks = add_inv_callbacks
        self.remove_inv_callbacks = remove_inv_callbacks
        self.buy_from_list = buy_from_list
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

        # container for sell, plus, and minus buttons
        self.sell_plus_minus_container = Frame(self)

        # sell button
        self.sell_button = Button(self.sell_plus_minus_container, text=sell_button_text, command=self.on_sell_click)

        # plus and minus buttons
        self.plus_button = Button(self.sell_plus_minus_container, text="+", command=self.plus_callback)
        self.minus_button = Button(self.sell_plus_minus_container, text="-", command=self.minus_callback)

        # variable objects frame and list, things like rating usually
        self.variables_frame = Frame(self)
        self.variables_dict = {}

        # spinbox for amounts
        amount_container = Frame(self)
        amount_label = Label(amount_container, text="Quantity:")
        self.amount_spinbox = Spinbox(amount_container, from_=1, to=float('inf'))

        # race mods
        self.race_mod_var = StringVar(value="None")

        self.race_mods_frame = ttk.LabelFrame(self, text="Race Mods")
        self.no_race_mod = Radiobutton(self.race_mods_frame, text="None", variable=self.race_mod_var, value="None")
        self.dwarf_race_mod = Radiobutton(self.race_mods_frame, text="Dwarf", variable=self.race_mod_var, value="Dwarf")
        self.troll_race_mod = Radiobutton(self.race_mods_frame, text="Troll", variable=self.race_mod_var, value="Troll")

        self.no_race_mod.pack(side=LEFT)
        self.dwarf_race_mod.pack(side=LEFT)
        self.troll_race_mod.pack(side=LEFT)

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
        self.object_library.grid                (column=0, row=0, sticky=(N, S), columnspan=2)
        self.object_library_scroll.grid         (column=2, row=0, sticky=(N, S))
        self.desc_box.grid                      (column=3, row=0, sticky=(N, S), columnspan=2)
        self.desc_box_scroll.grid               (column=5, row=0, sticky=(N, S))
        self.inventory_list.grid                (column=6, row=0, sticky=(N, S), columnspan=2)
        self.inventory_list_scroll.grid         (column=8, row=0, sticky=(N, S))

        self.sell_button.grid(column=0, row=0, sticky=N, padx=50)
        if plus_and_minus:
            self.plus_button.grid(column=1, row=0, sticky=N, padx=10, ipadx=3)
            self.minus_button.grid(column=2, row=0, sticky=N, padx=10, ipadx=3)

        self.buy_button.grid(column=0, row=1, sticky=N, columnspan=2)
        self.sell_plus_minus_container.grid(column=6, row=1, columnspan=2)

        self.variables_frame.grid(column=0, row=2)

        amount_label.pack(side=LEFT)
        self.amount_spinbox.pack(side=LEFT)

        if show_quantity:
            amount_container.grid(column=3, row=1)

        if show_race_mods:
            self.race_mods_frame.grid(column=3, row=2)

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

    # these two should only be overridden if they're actually used
    def plus_callback(self):
        pass

    def minus_callback(self):
        pass

    def fill_description_box(self, contents):
        """Clears the item description box and fills it with contents."""
        # temporarily unlock box, clear it, set the text, then re-lock it
        self.desc_box.config(state=NORMAL)
        self.desc_box.delete(1.0, END)
        self.desc_box.insert(END, contents)
        self.desc_box.config(state=DISABLED)

    def add_inv_item(self, item, listbox_string=print_name_and_options, count=1):
        """Adds item to the inventory this tab is linked to."""
        for i in range(count):
            self.statblock_inventory.append(item)
            self.inventory_list.insert(END, listbox_string(item))
        # callback functions
        for cb in self.add_inv_callbacks:
            cb()

    def remove_inv_item(self, index):
        """Removes an item at index from the inventory this tab is linked to."""
        del self.statblock_inventory[index]
        self.inventory_list.delete(index)

        # callback functions
        for cb in self.remove_inv_callbacks:
            cb()

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
        # clear the treeview selection
        self.object_library.selection_remove(self.object_library.selection())

        # for some reason this gets called when you swap the combobox with something selected on ProgramsTab
        # this shit exists just so we don't throw an error
        if len(self.inventory_list.curselection()) == 0:
            self.fill_description_box("")
            return

        item_report = self.statblock_inventory[self.inventory_list.curselection()[-1]].report()
        self.fill_description_box(item_report)

    def on_tree_item_click(self, event):
        # removing things from the selection causes these events to fire so we need to add this check
        # on the selection length to make sure we're not throwing errors
        if len(self.object_library.selection()) > 0:
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

            # deselect everything from the list
            self.inventory_list.selection_clear(0, END)

    def on_buy_click(self):
        # make sure we have something selected
        if len(self.object_library.selection()) > 0:
            selected_object = self.library_selected
        elif self.buy_from_list and len(self.inventory_list.curselection()) > 0:
            selected_object = self.statblock_inventory[self.inv_selected_index]
        else:
            print("Nothing is selected!")
            return

        # make sure what we have selected isn't None
        if selected_object is not None:
            # setup the dict for calculating attributes
            var_dict = {}
            for key in self.variables_dict.keys():
                var_dict[key] = self.variables_dict[key].get()

            # calculate any arithmetic expressions we have
            calculate_attributes(selected_object, var_dict, self.attributes_to_calculate)

            # find any "options" the item has and prompt the user to set them
            if "options" in selected_object.properties:
                option_entries = {}

                # define functions for ok and cancel
                def ok_func():
                    # set all of the options
                    for entry in option_entries:
                        selected_object.properties["options"][entry] = option_entries[entry].get()

                    self.buy_callback(selected_object)
                    temp_window.destroy()

                # if the user presses "cancel" then don't buy it
                def cancel_func():
                    temp_window.destroy()

                # setup new window
                temp_window = Toplevel(self.parent)
                temp_window.grab_set()
                temp_window.resizable(0, 0)

                # setup option labels and entries
                for option in selected_object.properties["options"]:
                    option_value = selected_object.properties["options"][option]
                    f = Frame(temp_window)
                    f.pack(side=TOP)
                    Label(f, text=option).pack(side=LEFT)
                    e = StringVar()
                    # make a combobox if it's a list
                    if type(option_value) is list:
                        ttk.Combobox(f, textvariable=e, state="readonly",
                                     values=copy(option_value))\
                            .pack(side=RIGHT, fill=X)
                    # make an entry if it's not
                    else:
                        Entry(f, textvariable=e).pack(side=RIGHT, fill=X)
                    option_entries[option] = e

                Button(temp_window, text="OK", command=ok_func).pack(side=LEFT)
                Button(temp_window, text="Cancel", command=cancel_func).pack(side=RIGHT)

            else:
                self.buy_callback(selected_object)
        else:
            print("Can't buy that!")

    def on_sell_click(self):
        # don't do anything if nothing is selected
        if len(self.inventory_list.curselection()) > 0:
            self.sell_callback(self.inv_selected_index)

    def update_inventory_text_at_index(self, index, text):
        was_selected = self.inventory_list.selection_includes(index)

        self.inventory_list.delete(index)
        self.inventory_list.insert(index, text)
        if was_selected:
            self.inventory_list.selection_set(index)

    @abstractmethod
    def on_switch(self):
        pass

    @abstractmethod
    def load_character(self):
        self.inventory_list.delete(0, END)
        for item in self.statblock_inventory:
            insert_value = print_name_and_options(item)
            self.inventory_list.insert(END, insert_value)
