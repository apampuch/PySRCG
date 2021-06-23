from copy import copy

from src import app_data
from src.CharData.power import Power
from src.Tabs.notebook_tab import NotebookTab
from src.utils import treeview_get, recursive_treeview_fill

from tkinter import *
from tkinter import ttk


class PowersTab(NotebookTab):
    @property
    def library_selected(self) -> Power:
        return treeview_get(self.powers_library, self.powers_library_dict)

    @property
    def list_selected(self) -> Power:
        return treeview_get(self.powers_list, self.statblock.powers)

    def __init__(self, parent):
        super().__init__(parent)

        self.powers_library_dict = {}

        self.powers_library = ttk.Treeview(self, height=20,
                                           columns=("cost", "page"),
                                           displaycolumns="#all")
        self.powers_library_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.powers_library.yview)
        self.powers_library.heading("#0", text="Name")
        self.powers_library.heading("#1", text="Cost")
        self.powers_library.heading("#2", text="Page")

        self.powers_library.column("#0", width=150, stretch=NO)
        self.powers_library.column("#1", width=50, stretch=NO)
        self.powers_library.column("#2", width=60)

        self.powers_list = ttk.Treeview(self, height=20,
                                        columns=("cost", "level", "page"),
                                        displaycolumns="#all")
        self.powers_list_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.powers_list.yview)
        self.powers_list.heading("#0", text="Name")
        self.powers_list.heading("#1", text="Cost")
        self.powers_list.heading("#2", text="Rank")
        self.powers_list.heading("#3", text="Page")

        self.powers_list.column("#0", width=150, stretch=NO)
        self.powers_list.column("#1", width=50, stretch=NO)
        self.powers_list.column("#2", width=50, stretch=NO)
        self.powers_list.column("#3", width=60)

        self.add_button = Button(self, text="Add", command=self.on_add_click)
        self.remove_button = Button(self, text="Remove", command=self.on_remove_click)
        self.plus_button = Button(self, text="+", command=self.on_plus_click)
        self.minus_button = Button(self, text="-", command=self.on_minus_click)

        # bind events
        self.powers_library["yscrollcommand"] = self.powers_library_scroll.set
        self.powers_list["yscrollcommand"] = self.powers_list_scroll.set

        self.powers_library.grid(column=0, row=0, sticky=(N, S))
        self.powers_library_scroll.grid(column=1, row=0, sticky=(N, S))
        self.powers_list.grid(column=2, row=0, sticky=(N, S))
        self.powers_list_scroll.grid(column=3, row=0, sticky=(N, S))

        self.add_button.grid(column=0, row=1, sticky=W)
        self.remove_button.grid(column=1, row=1, sticky=W)
        self.plus_button.grid(column=2, row=1, sticky=W)
        self.minus_button.grid(column=3, row=1, sticky=W)

        def power_tab_recurse_check(val):
            return "cost" not in val.keys()

        def power_tab_recurse_end_callback(key, val, iid):
            self.powers_library_dict[iid] = Power(name=key, **val)

        recursive_treeview_fill(self.parent.game_data["Powers"], "", self.powers_library,
                                power_tab_recurse_check, power_tab_recurse_end_callback, ("cost", "page"))

    def on_add_click(self):
        if self.library_selected is not None:
            # check to make sure it's not already there
            for power in self.statblock.powers:
                if power.name == self.library_selected.name:
                    print("Already known!")
                    return

            # current_essence = self.statblock.essence
            total_power_points = self.statblock.power_points

            print("Library Selected: " + self.library_selected.name)
            power = copy(self.library_selected)

            # make sure we have enough power points remaining
            if total_power_points + power.cost * power.level <= self.statblock.total_power_points:
                # if so, add to the character's statblock and UI
                self.statblock.powers.append(power)
                self.powers_list.insert("", END, text=power.name, values=(power.cost, power.level, power.page))

                # fix internal variable shit
                self.calculate_total()

            else:
                print("Not enough magic remaining!")

    def on_remove_click(self):
        # don't do anything if nothing is selected
        if self.list_selected is None:
            return

        # print("List selected: " + self.list_selected.name)
        for power in self.statblock.powers:
            # print("Power name: " + power.name)
            if power.name == self.list_selected.name:
                self.statblock.powers.remove(power)
                self.powers_list.delete(self.powers_list.selection())

                # fix internal variable shit
                self.calculate_total()

                return

        raise ValueError(self.list_selected.name + " not in self.statblock.powers.")

    def on_plus_click(self):
        selected = self.list_selected
        if selected is None:
            return

        base_cost = selected.cost / selected.level

        # TODO if max_levels == null pretend max_levels == magic attribute

        # TODO check if we're under max_levels

        if self.statblock.power_points + base_cost <= self.statblock.magic:
            selected.cost += base_cost
            selected.level += 1

            self.powers_list.set(self.powers_list.focus(), "cost", selected.cost)
            self.powers_list.set(self.powers_list.focus(), "level", selected.level)

            self.calculate_total()

        else:
            print("Not enough magic remaining!")

    def on_minus_click(self):
        selected = self.list_selected
        if selected is None:
            return

        base_cost = selected.cost / selected.level

        if selected.level > 1:
            selected.cost -= base_cost
            selected.level -= 1

            self.powers_list.set(self.powers_list.focus(), "cost", selected.cost)
            self.powers_list.set(self.powers_list.focus(), "level", selected.level)

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
        self.powers_list.delete(*self.powers_list.get_children())

        for power in self.statblock.powers:
            self.powers_list.insert("", END, text=power.name, values=(power.cost, power.level, power.page))

        self.calculate_total()
