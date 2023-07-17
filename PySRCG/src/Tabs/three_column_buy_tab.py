from copy import copy

from tkinter import *
from tkinter import ttk, messagebox

from typing import List, Callable

from src.CharData.power import Power
from src.Tabs.notebook_tab import NotebookTab
from src.statblock_modifier import StatMod
from src.utils import recursive_treeview_fill, treeview_get, get_variables, calculate_attributes

from abc import ABC, abstractmethod

"""
Some mods will have incomplete strings like cyber_ATTRIBUTE.
These will also have options corresponding to these. These all-caps strings are replaced with the selection
for that option. e.g. cyber_ATTRIBUTE will have an "Attribute": ["Strength", "Body", "Quickness"] property.
The user will choose one of those three (e.g. Body), and it will become "cyber_body".
Always lowercase the chosen option.
In the future, as things get more and more fucked, we may need to replace this with a separate list that
corresponds to the options 1:1 with their indices.
"""


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
        if len(selection) == 0:
            return None
        return selection[-1]

    def __init__(self, parent, name,
                 buy_button_text="Buy",
                 sell_button_text="Sell",
                 add_inv_callbacks: List[Callable] = None,      # callback functions when adding to inventory
                 remove_inv_callbacks: List[Callable] = None,   # callback functions when removing from inventory
                 treeview_get_make_copy=True,
                 show_quantity=False,
                 show_race_mods=False,
                 buy_from_list=False,
                 show_cyberware_grades=False,
                 show_bioware_grades=False,
                 plus_and_minus=False):  # allow buying the selected object from the inventory list

        # allow purchasing of duplicate items if False, set True in subclass init to disallow
        self.no_duplicates = False

        if add_inv_callbacks is None:
            add_inv_callbacks = []

        if remove_inv_callbacks is None:
            remove_inv_callbacks = []

        super().__init__(parent, name)
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

        # cyberware grades
        self.grade_var = StringVar(value="standard")
        self.cyberware_grade_frame = LabelFrame(self, text="Grade")
        self.standard_radio = Radiobutton(self.cyberware_grade_frame,
                                          text="Standard",
                                          variable=self.grade_var,
                                          value="standard")
        self.alpha_radio = Radiobutton(self.cyberware_grade_frame,
                                       text="Alphaware",
                                       variable=self.grade_var,
                                       value="alpha")
        self.beta_radio = Radiobutton(self.cyberware_grade_frame,
                                      text="Betaware",
                                      variable=self.grade_var,
                                      value="beta")
        self.delta_radio = Radiobutton(self.cyberware_grade_frame,
                                       text="Deltaware",
                                       variable=self.grade_var,
                                       value="delta")

        self.standard_radio.pack(side=LEFT)
        self.alpha_radio.pack(side=LEFT)
        self.beta_radio.pack(side=LEFT)
        self.delta_radio.pack(side=LEFT)

        self.bio_grade_var = StringVar(value="standard")
        self.bioware_grade_frame = LabelFrame(self, text="Grade")
        self.bio_standard_radio = Radiobutton(self.bioware_grade_frame,
                                              text="Standard",
                                              variable=self.bio_grade_var,
                                              value="standard")
        self.bio_cultured_radio = Radiobutton(self.bioware_grade_frame,
                                              text="Cultured",
                                              variable=self.bio_grade_var,
                                              value="cultured")

        self.bio_standard_radio.pack(side=LEFT)
        self.bio_cultured_radio.pack(side=LEFT)

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
        self.object_library.grid                (column=0, row=0, sticky=NS, columnspan=2)
        self.object_library_scroll.grid         (column=2, row=0, sticky=NS)
        self.desc_box.grid                      (column=3, row=0, sticky=NS, columnspan=2)
        self.desc_box_scroll.grid               (column=5, row=0, sticky=NS)
        self.inventory_list.grid                (column=6, row=0, sticky=NS, columnspan=2)
        self.inventory_list_scroll.grid         (column=8, row=0, sticky=NS)

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

        if show_cyberware_grades:
            self.cyberware_grade_frame.grid(column=3, row=2)

        if show_bioware_grades:
            self.bioware_grade_frame.grid(column=3, row=2)

    def reload_data(self):
        children = self.object_library.get_children()
        self.object_library.delete(*children)
        recursive_treeview_fill(self.library_source, "", self.object_library,
                                self.recurse_check_func, self.recurse_end_func)

    @property
    @abstractmethod
    def library_source(self):
        """The thing that the library needs to be filled from."""
        pass

    @property
    @abstractmethod
    def statblock_inventory(self):
        """The inventory in the statblock that contains this."""
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

    @staticmethod
    def name_for_list(x):
        """This should be overridden in some cases."""
        ret = f"{x.properties['name']} "
        if "options" in x.properties:
            for option in x.properties["options"].values():
                ret += f"({option}) "

        return ret.rstrip()

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

    def add_inv_item(self, item, count=1):
        """Adds item to the inventory this tab is linked to."""

        # warning if adding more than 1 count and it has mods
        if "mods" in item.properties and count > 1:
            messagebox.showwarning(title="Warning",
                                   message=f"Adding {count} copies of an item with mods. This may cause bugs.")

        for i in range(count):
            self.statblock_inventory.append(item)
            self.inventory_list.insert(END, self.name_for_list(item))

            # add mods from item into global StatMod container
            if "mods" in item.properties:
                for key in item.properties["mods"].keys():
                    value = item.properties["mods"][key]

                    # check if value is a string, if so, it should be a key in item.properties that resolves to a number
                    if type(value) is str:
                        if value not in item.properties:
                            messagebox.showerror(title="Error", message=f"{value} not in {item.properties['name']}!")
                            raise ValueError(f"{value} not in {item.properties['name']}!")
                        elif type(item.properties[value]) is not int:
                            messagebox.showerror(title="Error",
                                                 message=f"{value} in {item.properties['name']} is not an integer!")

                            raise ValueError(f"{value} in {item.properties['name']} is not an integer!")
                        else:
                            value = item.properties[value]
                    StatMod.add_mod(key, value)

        # callback functions
        for cb in self.add_inv_callbacks:
            cb()

    def remove_inv_item(self, index):
        """Removes an item at index from the inventory this tab is linked to."""
        item = self.statblock_inventory[index]

        # delete mods if they exist
        if "mods" in item.properties.keys():
            for key in item.properties["mods"].keys():
                value = item.properties["mods"][key]

                StatMod.remove_mod(key, value)

        del self.statblock_inventory[index]
        self.inventory_list.delete(index)

        # callback functions
        for cb in self.remove_inv_callbacks:
            cb()

    def check_for_duplicates(self, to_buy):
        if not self.no_duplicates:
            return True

        # convert to set for sweet O(1) lookups
        set_list = set(self.statblock_inventory)

        # return True if no duplicates were found
        return to_buy not in set_list

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
    def on_tree_item_click(self, event):
        # removing things from the selection causes these events to fire, so we need to add this check
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
                if "attributes_to_calculate" in selected_item.properties:
                    self.variables_dict = get_variables(selected_item,
                                                        selected_item.properties["attributes_to_calculate"])
                else:
                    self.variables_dict = {}

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

            # manually add power level to var_dict if it's an adept power
            if type(selected_object) is Power:
                var_dict["power_level"] = 1

            # TODO unfuck this by doing the window check at the start and making the ok func call this again but not \
            # open the window, add a force_ignore_window arg maybe?

            # find any "options" the item has and prompt the user to set them
            if "options" in selected_object.properties:
                option_entries = {}

                # define functions for ok and cancel
                def ok_func():
                    # set all the options
                    for entry in option_entries:
                        if option_entries[entry].get() == "":
                            messagebox.showerror(title="Error", message="No blank options allowed.")
                            temp_window.destroy()
                            return

                    for entry in option_entries:
                        selected_object.properties["options"][entry] = option_entries[entry].get()
                        chosen_option_key = str.upper(entry)
                        chosen_option_val = str.lower(selected_object.properties["options"][entry])

                        # if we have mods, replace any ambiguities in mods with the chosen option
                        if "mods" in selected_object.properties:
                            for old_key in selected_object.properties["mods"]:
                                # replace "attribute" with the correct attribute in something like "cyber_attribute"
                                if chosen_option_key in old_key:
                                    val = selected_object.properties["mods"][old_key]
                                    new_key = old_key.replace(chosen_option_key, chosen_option_val)
                                    selected_object.properties["mods"][new_key] = val
                                    del selected_object.properties["mods"][old_key]

                    if not self.check_for_duplicates(selected_object):
                        messagebox.showerror(title="Error", message="No duplicates allowed.")
                        raise ValueError("No duplicates allowed.")

                    # calculate any arithmetic expressions we have
                    # TODO get level into var_dict somehow
                    if "attributes_to_calculate" in selected_object.properties:
                        calculate_attributes(selected_object, var_dict,
                                             selected_object.properties["attributes_to_calculate"])

                    self.buy_callback(selected_object)
                    temp_window.destroy()

                # if the user presses "cancel" then don't buy it
                def cancel_func():
                    temp_window.destroy()

                # setup new window
                temp_window = Toplevel(self.parent)
                temp_window.grab_set()
                temp_window.resizable(False, False)

                # setup option labels and entries
                for option in selected_object.properties["options"]:
                    option_value = selected_object.properties["options"][option]
                    f = Frame(temp_window)
                    f.pack(side=TOP)
                    Label(f, text=option).pack(side=LEFT)
                    e = StringVar()
                    # make a combobox if it's a list
                    if type(option_value) is list:
                        new_box = ttk.Combobox(f, textvariable=e, state="readonly", values=copy(option_value))
                        new_box.current(0)
                        new_box.pack(side=RIGHT, fill=X)
                    # make an entry if it's not
                    else:
                        Entry(f, textvariable=e).pack(side=RIGHT, fill=X)
                    option_entries[option] = e

                Button(temp_window, text="OK", command=ok_func).pack(side=LEFT)
                Button(temp_window, text="Cancel", command=cancel_func).pack(side=RIGHT)

            else:
                # calculate any arithmetic expressions we have
                if "attributes_to_calculate" in selected_object.properties:
                    calculate_attributes(selected_object, var_dict,
                                         selected_object.properties["attributes_to_calculate"])

                if not self.check_for_duplicates(selected_object):
                    messagebox.showerror(title="Error", message="No duplicates allowed.")
                    raise ValueError("No duplicates allowed.")
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
        # refesh the list on switch
        # hopefully this doesn't cause any bugs
        self.inventory_list.delete(0, END)
        for item in self.statblock_inventory:
            insert_value = self.name_for_list(item)
            self.inventory_list.insert(END, insert_value)

    @abstractmethod
    def load_character(self):
        self.on_switch()
