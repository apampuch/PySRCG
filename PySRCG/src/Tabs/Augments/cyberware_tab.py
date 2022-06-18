from copy import copy
from tkinter import *
from tkinter import ttk

from src import app_data
from src.CharData.augment import Cyberware
from src.Tabs.notebook_tab import NotebookTab
from src.statblock_modifier import StatMod
from src.utils import treeview_get, recursive_treeview_fill, calculate_attributes, get_variables

# list of attributes that we need to look for variables in, eg "Cost: rating * 500"
ATTRIBUTES_TO_CALCULATE = ["essence", "cost", "availability_rating", "availability_time", "mods"]
STRINGS_TO_IGNORE = []  # nyi


class CyberwareTab(NotebookTab):
    @property
    def library_selected(self):
        return treeview_get(self.cyberware_library, self.tree_library_dict)

    @property
    def list_selected_index(self) -> int:
        """index of the index of the selected item"""
        selection = self.cyberware_list.curselection()
        if len(selection) == 0:
            return None
        return selection[-1]

    def __init__(self, parent):
        super().__init__(parent)

        # used to validate input
        self.vcmd = (self.register(self.int_validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.tree_library_dict = {}  # maps library terminal children iids to (skill name, skill attribute) tuple

        # cyberware library
        self.cyberware_library = ttk.Treeview(self, height=20, show="tree")
        self.cyberware_library_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.cyberware_library.yview)

        # cyberware list
        self.cyberware_list = Listbox(self, width=40)
        self.cyberware_list_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.cyberware_list.yview)

        # description box
        self.desc_box = Text(self, width=40, state=DISABLED, bg='#d1d1d1')
        self.desc_box_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.desc_box.yview)

        # radio boxes
        self.grade_var = StringVar()
        self.grade_frame = LabelFrame(self, text="Grade")
        self.standard_radio = Radiobutton(self.grade_frame,
                                          text="Standard",
                                          variable=self.grade_var,
                                          value="standard")
        self.alpha_radio = Radiobutton(self.grade_frame,
                                       text="Alphaware",
                                       variable=self.grade_var,
                                       value="alpha")
        self.beta_radio = Radiobutton(self.grade_frame,
                                      text="Betaware",
                                      variable=self.grade_var,
                                      value="beta")
        self.delta_radio = Radiobutton(self.grade_frame,
                                       text="Deltaware",
                                       variable=self.grade_var,
                                       value="delta")

        # buttons
        self.buy_sell_frame = Frame(self)
        self.buy_button = Button(self.buy_sell_frame, text="Buy", command=self.on_buy_click)
        self.sell_button = Button(self.buy_sell_frame, text="Sell", command=self.on_sell_click)

        # variable objects frame and list
        self.variables_frame = Frame(self)
        self.variables_dict = {}

        # bind events
        self.cyberware_library["yscrollcommand"] = self.cyberware_library_scroll.set
        self.cyberware_library.bind("<<TreeviewSelect>>", self.on_tree_item_click)
        self.cyberware_list["yscrollcommand"] = self.cyberware_list_scroll.set
        self.cyberware_list.bind("<<ListboxSelect>>", self.on_inv_item_click)
        self.desc_box["yscrollcommand"] = self.desc_box_scroll.set

        # grids
        self.cyberware_library.grid(column=0, row=0, sticky=(N, S))
        self.cyberware_library_scroll.grid(column=1, row=0, sticky=(N, S))

        self.desc_box.grid(column=3, row=0, sticky=(N, S))
        self.desc_box_scroll.grid(column=4, row=0, sticky=(N, S))

        self.cyberware_list.grid(column=5, row=0, sticky=(N, S))
        self.cyberware_list_scroll.grid(column=6, row=0, sticky=(N, S))

        self.buy_sell_frame.grid(column=5, row=1, sticky=E)
        self.buy_button.grid(column=0, row=0, sticky=W)
        self.sell_button.grid(column=1, row=0, sticky=W)

        self.grade_frame.grid(column=0, row=1, sticky=W, columnspan=4)

        self.standard_radio.grid(column=0, row=0)
        self.alpha_radio.grid(column=1, row=0)
        self.beta_radio.grid(column=2, row=0)
        self.delta_radio.grid(column=3, row=0)
        self.standard_radio.select()
        self.standard_radio.invoke()

        self.variables_frame.grid(column=0, row=3)

        recursive_treeview_fill(self.library_source, "", self.cyberware_library,
                                self.recurse_check_func, self.recurse_end_func)

    @property
    def recurse_check_func(self):
        def augment_tab_recurse_check(val):
            return "essence" not in val.keys()

        return augment_tab_recurse_check

    @property
    def recurse_end_func(self):
        def augment_tab_recurse_end_callback(key, val, iid):
            # key is a string
            # val is a _dict from a json
            try:
                self.tree_library_dict[iid] = Cyberware(name=key, **val)
            except TypeError as e:
                print("Error with cyberware {}:".format(key))
                print(e)
                print()

        return augment_tab_recurse_end_callback

    @property
    def library_source(self):
        try:
            return self.parent.game_data["Augments"]["Cyberware"]
        except KeyError:
            return {}

    def on_buy_click(self):
        if self.library_selected is not None:
            current_essence = self.statblock.essence

            # make copies of info we need to copy from the _dict
            cyber: Cyberware = self.library_selected
            cyber.add_field("grade", str(self.grade_var.get()))

            # make a new _dict from the variables _dict that we can pass into parse_arithmetic()
            # because parse_arithmetic() can't take IntVars
            var_dict = {}
            for key in self.variables_dict.keys():
                var_dict[key] = self.variables_dict[key].get()

            # calculate any arithmetic expressions we have
            if "attributes_to_calculate" in cyber.properties:
                calculate_attributes(cyber, var_dict, cyber.properties["attributes_to_calculate"])

            cyber.properties["essence"] = self.calc_essence_cost(cyber, cyber.properties["grade"])
            cyber.properties["cost"] = int(self.calc_yen_cost(cyber, cyber.properties["grade"]))

            # if we have enough essence
            if cyber.properties["essence"] < current_essence:
                # if we have enough money
                if app_data.pay_cash(cyber.properties["cost"]):
                    self.add_cyberware_item(cyber)
                    self.calculate_total()
            else:
                print("Not enough essence left!")

        else:
            print("Can't get that!")

    def on_sell_click(self):
        # don't do anything if nothing is selected
        if len(self.cyberware_list.curselection()) == 0:
            return

        # return cash value
        # self.statblock.cash += self.statblock.cyberware[self.list_selected_index].properties["cost"]
        self.statblock.add_cash(self.statblock.cyberware[self.list_selected_index].properties["cost"])

        self.remove_cyberware_item(self.list_selected_index)
        self.calculate_total()

    def add_cyberware_item(self, cyber):
        """
        Adds a cyberware item to the character, applies any mods the cyberware has.
        :type cyber: Cyberware
        """
        if "mods" in cyber.properties:
            for key in cyber.properties["mods"].keys():
                value = cyber.properties["mods"][key]
                StatMod.add_mod(key, value)
        self.statblock.cyberware.append(cyber)
        self.cyberware_list.insert(END, cyber.name)

    def remove_cyberware_item(self, index):
        cyber = self.statblock.cyberware[index]
        if "mods" in cyber.properties:
            for key in cyber.properties["mods"].keys():
                value = cyber.properties["mods"][key]
                StatMod.remove_mod(key, value)

        del self.statblock.cyberware[index]
        self.cyberware_list.delete(index)

    def calc_essence_cost(self, cyber, grade):
        essence = cyber.properties["essence"]

        if grade == "standard":
            pass
        elif grade == "alpha":
            essence *= 0.8
        elif grade == "beta":
            essence *= 0.6
        elif grade == "delta":
            essence *= 0.5
        else:
            raise ValueError("Invalid grade {}.".format(grade))

        return essence

    def calc_yen_cost(self, cyber, grade):
        cost = cyber.properties["cost"]

        if grade == "standard":
            pass
        elif grade == "alpha":
            cost *= 2
        elif grade == "beta":
            cost *= 4
        elif grade == "delta":
            cost *= 8
        else:
            raise ValueError("Invalid grade {}.".format(grade))

        return cost

    def fill_description_box(self, contents):
        """Clears the item description box and fills it with contents."""
        # temporarily unlock box, clear it, set the text, then re-lock it
        self.desc_box.config(state=NORMAL)
        self.desc_box.delete(1.0, END)
        self.desc_box.insert(END, contents)
        self.desc_box.config(state=DISABLED)

    def on_tree_item_click(self, event):
        # only select the last one selected if we've selected multiple things
        selected = self.cyberware_library.selection()[-1]
        if selected in self.tree_library_dict.keys():
            selected_cyberware = self.tree_library_dict[selected]
            self.fill_description_box(selected_cyberware.report())

            # destroy all variable objects
            self.variables_dict = {}
            for child in self.variables_frame.winfo_children():
                child.destroy()

            # get any variables in the item
            if "attributes_to_calculate" in selected_cyberware.properties:
                self.variables_dict = get_variables(selected_cyberware,
                                                    selected_cyberware.properties["attributes_to_calculate"])
            else:
                self.variables_dict = {}

            # make variable objects if any
            i = 0
            for var in self.variables_dict.keys():
                var_frame = Frame(self.variables_frame)
                Label(var_frame, text="{}:".format(var)).grid(column=0, row=0)  # label
                Entry(var_frame, textvariable=self.variables_dict[var], validate="key", validatecommand=self.vcmd) \
                    .grid(column=1, row=0)
                var_frame.grid(column=0, row=i)
                i += 1

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
        # this gets called when changing races sometimes
        # this condition should shut it up
        if len(self.cyberware_list.curselection()) > 0:
            curselection_ = self.cyberware_list.curselection()[-1]
            item_report = self.statblock.cyberware[curselection_].report()
            self.fill_description_box(item_report)

    def calculate_total(self):
        # unlike the other tabs places we directly manipulate the top bar
        # since this has nothing to do with the generation mode
        app_data.top_bar.update_karma_bar("{:.2f}".format(self.statblock.essence),
                                          self.statblock.base_attributes["essence"],
                                          "Augments Tab")
        # app_data.top_bar.karma_fraction.set(("{}/{}".format("{:.2f}".format(self.statblock.essence),
        #                                     self.statblock.base_attributes["essence"])))

    def reload_data(self):
        children = self.cyberware_library.get_children()
        self.cyberware_library.delete(*children)
        recursive_treeview_fill(self.library_source, "", self.cyberware_library,
                                self.recurse_check_func, self.recurse_end_func)

    def on_switch(self):
        self.calculate_total()

    def load_character(self):
        # clear everything
        # self.tree_library_dict = {}
        self.cyberware_list.delete(0, END)

        # add stuff to the list
        for cyber in self.statblock.cyberware:
            self.cyberware_list.insert(END, cyber.name)

        # self.on_switch()
