from abc import ABC
from copy import copy
from tkinter import *
from tkinter import ttk

from src import app_data
from src.CharData.metamagic import Metamagic
from src.CharData.ordeal import Ordeal
from src.CharData.tradition import Tradition
from src.GenModes.finalized import Finalized
from src.Tabs.notebook_tab import NotebookTab
from src.adjustment import Adjustment


class MagicBackgroundTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "MagicBackgroundTab")

        # formatting
        self.rowconfigure(2, weight=9)  # to make the rows look nice and stack perfectly

        # the tradition box should be unchanging
        self.traditions_labelframe = ttk.LabelFrame(self, text="Tradition")
        self.tradition_box = ttk.Combobox(self.traditions_labelframe, state="readonly")
        self.tradition_box.bind("<<ComboboxSelected>>", self.on_change_tradition)
        self.tradition_box.grid(column=0, row=0)

        # setup and populate tradition _dict
        self.traditions_dict = None

        # aspects combobox
        self.focus_aspects = []
        self.aspects_labelframe = ttk.LabelFrame(self, text="Aspect")
        self.aspects_box = ttk.Combobox(self.aspects_labelframe, values=[], state="readonly")
        self.aspects_box.bind("<<ComboboxSelected>>", self.on_change_aspect)
        self.aspects_box.grid(column=0, row=0)

        # combobox for the focus
        self.focus_labelframe = ttk.LabelFrame(self, text="Focus")
        self.focus_box = ttk.Combobox(self.focus_labelframe, values=[], state="readonly")
        self.focus_box.bind("<<ComboboxSelected>>", self.on_change_focus)
        self.focus_box.grid(column=0, row=0)

        # listbox for geasa
        self.geasa_labelframe = ttk.LabelFrame(self, text="Geasa")
        self.geasa_listbox = Listbox(self.geasa_labelframe, width=40, height=7, selectmode=SINGLE)
        self.geasa_scroll = Scrollbar(self.geasa_labelframe, orient="vertical", command=self.geasa_listbox.yview)
        self.geasa_listbox["yscrollcommand"] = self.geasa_scroll.set
        self.new_button = ttk.Button(self.geasa_labelframe, text="New", command=self.new_geas)
        self.edit_button = ttk.Button(self.geasa_labelframe, text="Edit", command=self.edit_geas)
        self.delete_button = ttk.Button(self.geasa_labelframe, text="Delete", command=self.delete_geas)

        self.geasa_listbox.grid(column=0, row=0, rowspan=3)
        self.geasa_scroll.grid(column=1, row=0, rowspan=3, sticky=NS)
        self.new_button.grid(column=2, row=0, padx=5)
        self.edit_button.grid(column=2, row=1, padx=5)
        self.delete_button.grid(column=2, row=2, padx=5)

        # initiation stuff
        self.initiations_labelframe = ttk.LabelFrame(self, text="Initiations")
        self.initiations_listbox = Listbox(self.initiations_labelframe, height=10)

        # group stuff
        self.group_labelframe = ttk.LabelFrame(self, text="Groups")
        self.group_listbox = Listbox(self.group_labelframe, height=8)

        self.join_button = Button(self.group_labelframe, text="Join", command=self.join_group)
        self.edit_group_button = Button(self.group_labelframe, text="Edit", command=self.edit_group)
        self.leave_button = Button(self.group_labelframe, text="Leave", command=self.leave_group)

        # purchase options
        self.purchase_labelframe = ttk.LabelFrame(self, text="New Initiation", width=6000)
        # self vs group initiation
        self.self_group_var = StringVar()
        self.self_group_var.set("self")
        self.self_radio = Radiobutton(self.purchase_labelframe, text="Self Initiation", variable=self.self_group_var,
                                      value="self", command=self.update_karma_cost)
        self.group_radio = Radiobutton(self.purchase_labelframe, text="Group Initiation", variable=self.self_group_var,
                                       value="group", command=self.update_karma_cost)

        # ordeal
        self.ordeal_var = IntVar()
        self.ordeal_var.set(0)
        self.ordeal_checkbox = Checkbutton(self.purchase_labelframe, text="Ordeal", variable=self.ordeal_var,
                                           command=self.update_karma_cost)

        # karma cost label
        self.karma_cost_label = Label(self.purchase_labelframe, text="Karma Cost")
        self.karma_cost_var = StringVar()
        self.karma_cost_var.set("0")
        self.karma_cost_box = Entry(self.purchase_labelframe, textvariable=self.karma_cost_var, state="disabled",
                                    width=4)

        # buy button
        self.buy_button = Button(self.purchase_labelframe, text="Initiate", command=self.add_initiation)
        self.sell_button = Button(self.purchase_labelframe, text="Delete", command=self.delete_initiation)

        self.self_radio.grid(column=0, row=0, sticky=W)
        self.group_radio.grid(column=0, row=1, sticky=W)
        self.ordeal_checkbox.grid(column=0, row=2, sticky=W)
        self.karma_cost_label.grid(column=0, row=3, sticky=W)
        self.karma_cost_box.grid(column=1, row=3, sticky=W)
        self.buy_button.grid(column=0, row=4, sticky=W)

        # initiation benefit
        self.benefit_labelframe = ttk.LabelFrame(self, text="Benefit")
        # radiobutton var
        self.benefit_var = StringVar()
        self.benefit_var.set("new_metamagic")
        self.new_metamagic_button = Radiobutton(self.benefit_labelframe, text="Learn New Metamagic",
                                                variable=self.benefit_var, value="new_metamagic")
        self.alter_signature_button = Radiobutton(self.benefit_labelframe, text="Alter Astral Signature",
                                                  variable=self.benefit_var, value="alter_signature")
        self.shed_geas_button = Radiobutton(self.benefit_labelframe, text="Shed Geas",
                                            variable=self.benefit_var, value="shed_geas")

        self.new_metamagic_button.grid(column=0, row=0)
        self.alter_signature_button.grid(column=0, row=1)
        self.shed_geas_button.grid(column=0, row=2)

        self.ordeal_library = []
        self.ordeal_labelframe = ttk.LabelFrame(self, text="Ordeal")
        self.ordeal_listbox = Listbox(self.ordeal_labelframe, height=8, exportselection=0)
        self.ordeal_scroll = Scrollbar(self.ordeal_labelframe, orient="vertical", command=self.ordeal_listbox.yview)
        self.ordeal_listbox["yscrollcommand"] = self.ordeal_scroll.set
        self.ordeal_listbox.grid(column=0, row=0)
        self.ordeal_scroll.grid(column=1, row=0, sticky=NS)

        self.metamagic_library = []
        self.metamagic_labelframe = ttk.LabelFrame(self, text="Metamagic")
        self.metamagic_listbox = Listbox(self.metamagic_labelframe, height=8, exportselection=0)
        self.metamagic_scroll = Scrollbar(self.metamagic_labelframe, orient="vertical",
                                          command=self.metamagic_listbox.yview)
        self.metamagic_listbox["yscrollcommand"] = self.metamagic_scroll.set
        self.metamagic_listbox.grid(column=0, row=0)
        self.metamagic_scroll.grid(column=1, row=0, sticky=NS)

        self.initiations_listbox.grid(column=0, row=0, sticky=EW)
        self.group_listbox.grid(column=0, row=0, columnspan=3, sticky=EW)
        self.join_button.grid(column=0, row=1, sticky=W, padx=10, pady=2)
        self.edit_group_button.grid(column=1, row=1, sticky=W, padx=10, pady=2)
        self.leave_button.grid(column=2, row=1, sticky=E, padx=10, pady=2)

        # top row
        self.traditions_labelframe.grid(column=0, row=0, columnspan=3, sticky=N)
        self.geasa_labelframe.grid(column=3, row=0, columnspan=9, rowspan=3, sticky=EW)

        # mid row
        self.initiations_labelframe.grid(column=0, row=3, columnspan=6, sticky=EW)
        self.initiations_labelframe.columnconfigure(0, weight=1)
        self.group_labelframe.grid(column=6, row=3, columnspan=6, sticky=NSEW)
        self.group_labelframe.columnconfigure(0, weight=1)
        self.group_labelframe.columnconfigure(1, weight=1)

        # bot row
        self.purchase_labelframe.grid(column=0, row=4, columnspan=3, sticky=NS)
        self.benefit_labelframe.grid(column=3, row=4, columnspan=3, sticky=NS)
        self.ordeal_labelframe.grid(column=6, row=4, columnspan=3, sticky=NS)
        self.metamagic_labelframe.grid(column=9, row=4, columnspan=3, sticky=NS)

        self.reload_data()

    # noinspection PyUnusedLocal
    def on_change_tradition(self, *args):
        self.statblock.tradition = self.traditions_dict[self.tradition_box.get()]
        self.fill_aspects()
        self.check_focus_box()

        # clear aspect if it's invalid
        if self.statblock.aspect not in self.statblock.tradition.allowed_aspects:
            self.statblock.aspect = None
            self.aspects_box.set("")

        # clear focus no matter what
        self.focus_box.set("")

    # noinspection PyUnusedLocal
    def on_change_aspect(self, *args):
        self.statblock.aspect = self.aspects_box.get()
        self.check_focus_box()

        # clear the focus if it's not kosher
        if not self.statblock.tradition.always_has_focus and self.statblock.aspect not in self.focus_aspects:
            self.focus_box.set("")

    def prompt_window(self, ok_func, label, insert=None):        # setup new window
        ask_window = Toplevel(self.parent)
        ask_window.grab_set()
        ask_window.resizable(None, None)

        prompt_entry = Entry(ask_window)

        if insert is not None:
            insert(prompt_entry)

        def cancel_func():
            ask_window.destroy()

        Label(ask_window, text=label).pack()
        prompt_entry.pack(fill=X)
        Button(ask_window, text="OK", command=lambda: ok_func(prompt_entry, ask_window)).pack(side=LEFT)
        Button(ask_window, text="Cancel", command=cancel_func).pack(side=RIGHT)

    def new_geas(self):
        # check if we even CAN get a new geas
        if self.statblock.magic >= self.statblock.essence:
            print("Can't take a geas.")
            return

        def ok_func(entry, window):
            new_geas = entry.get()
            self.statblock.geasa.append(new_geas)
            self.geasa_listbox.insert(END, new_geas)
            window.destroy()

        self.prompt_window(ok_func, "Geas ")

    def edit_geas(self):
        # do nothing if nothing is selected
        if len(self.geasa_listbox.curselection()) == 0:
            return

        selection = self.geasa_listbox.curselection()[0]

        def insert(entry):
            entry.insert(0, self.geasa_listbox.get(selection))

        def ok_func(entry, window):
            self.statblock.geasa[selection] = entry.get()
            self.geasa_listbox.delete(selection)
            self.geasa_listbox.insert(selection, entry.get())
            window.destroy()

        self.prompt_window(ok_func, "Geas ", insert)

    def delete_geas(self):
        # do nothing if nothing is selected
        if len(self.geasa_listbox.curselection()) == 0:
            return

        self.geasa_listbox.delete(self.geasa_listbox.curselection()[0])

    def join_group(self):
        if type(self.statblock.gen_mode) is not Finalized:
            print("Must be finalized!")
            return

        # charge 3 karma
        if self.statblock.gen_mode.point_purchase_allowed(3, None):
            def ok_func(entry, window):
                new_group = entry.get()

                # key should not matter because it's always 3 karma
                key = "join_group"
                adjustment = Adjustment(3, key, lambda: None)
                self.statblock.gen_mode.add_adjustment(adjustment)

                self.statblock.magical_groups.append(new_group)
                self.group_listbox.insert(END, new_group)
                window.destroy()

            self.prompt_window(ok_func, "Group Name ")
        else:
            print("Not enough karma!")

    def edit_group(self):
        # do nothing if nothing is selected
        if len(self.group_listbox.curselection()) == 0:
            return

        selection = self.group_listbox.curselection()[0]

        def insert(entry):
            entry.insert(0, self.group_listbox.get(selection))

        def ok_func(entry, window):
            self.statblock.magical_groups[selection] = entry.get()
            self.group_listbox.delete(selection)
            self.group_listbox.insert(selection, entry.get())
            window.destroy()

        self.prompt_window(ok_func, "Group Name ", insert)

    def leave_group(self):
        if len(self.group_listbox.curselection()) == 0:
            return

        sel = self.group_listbox.curselection()[0]

        # check if we have an adjustment and undo it if we do
        key = "join_group"
        self.statblock.gen_mode.undo(key)
        self.group_listbox.delete(sel)

    def add_initiation(self):
        # check that we're finalized
        if type(self.statblock.gen_mode) is not Finalized:
            print("Must be finalized!")
            return

        # check we have enough karma
        karma_cost = self.calc_karma_cost()
        if self.statblock.gen_mode.point_purchase_allowed(karma_cost, "initiate_grade"):
            # if group initiation, make sure a group is selected
            if self.self_group_var.get() == "group" and len(self.group_listbox.curselection()) == 0:
                print("Need to select a group to initiate with.")
                return

            # if ordeal, make sure an ordeal is selected
            if self.ordeal_var.get() and len(self.ordeal_listbox.curselection()) == 0:
                print("Need to select an ordeal to initiate with.")
                return

            # if metamagic, make sure a metamagic is selected
            if self.benefit_var.get() == "new_metamagic" and len(self.metamagic_listbox.curselection()) == 0:
                print("Need to select a metamagic to learn.")
                return

            # if shed_geas, make sure a geas is selected
            if self.benefit_var.get() == "shed_geas" and len(self.geasa_listbox.curselection()) == 0:
                print("Need to select a geas to shed.")
                return

            # build the string
            initiation_string = ""
            if self.self_group_var.get() == "self":
                initiation_string += "Self Initiation"
            elif self.self_group_var.get() == "group":
                initiation_string += "Group Initiation with "
                initiation_string += self.group_listbox.get(self.group_listbox.curselection()[0]) + " "
            else:
                raise ValueError(f"Invalid self_group_var: {self.self_group_var}")

            # add ordeal
            if self.ordeal_var.get():
                ordeal_index = self.ordeal_listbox.curselection()[0]
                ordeal = self.ordeal_library[ordeal_index]

                initiation_string += f"through {ordeal.name}"

            initiation_string += ": "

            if self.benefit_var.get() == "new_metamagic":
                metamagic_index = self.metamagic_listbox.curselection()[0]
                metamagic = self.metamagic_library[metamagic_index]

                # check to see if we already know a metamagic
                if metamagic.name in map(lambda x: x.name, self.statblock.metamagic):
                    print("Already know that metamagic!")
                    return

                # check to see if we know the metamagic's requirements
                # this is untested
                if "requirements" in metamagic.properties:
                    known = set(map(lambda x: x.name, self.statblock.metamagic))
                    requirements = set(metamagic.properties["requirements"])
                    if not known <= requirements:
                        need = requirements - known
                        print(f"Need {need} to learn {metamagic.name}.")

                self.statblock.metamagic.append(copy(metamagic))
                initiation_string += f"Learned {metamagic.name}"
            elif self.benefit_var.get() == "alter_signature":
                initiation_string += "Altered Signature"
            elif self.benefit_var.get() == "shed_geas":
                index = self.geasa_listbox.curselection()[0]
                geas = self.geasa_listbox.get(index)

                del self.statblock.geasa[index]
                self.geasa_listbox.delete(index)

                initiation_string += f"Shed {geas}"
            else:
                raise ValueError(f"Invalid benefit_var: {self.benefit_var.get()}")

            # add karma cost to sting
            initiation_string += f" ({karma_cost})"

            self.statblock.initiations.append(initiation_string)
            self.initiations_listbox.insert(END, initiation_string)
            adjustment = Adjustment(karma_cost, "initiate_grade", lambda x: None)
            self.statblock.gen_mode.add_adjustment(adjustment)
            self.update_karma_cost()
        else:
            print("Not enough karma!")

    def delete_initiation(self):
        # I will only allow LIFO deleting to make things sane
        pass

    # noinspection PyUnusedLocal
    def on_change_focus(self, *args):
        self.statblock.focus = self.focus_box.get()

    def fill_aspects(self):
        # get the aspects
        aspects = list(self.statblock.tradition.allowed_aspects)

        # some aspects have focuses and some don't in some traditions
        # for those, they have asterisks in their name
        self.focus_aspects.clear()
        if not self.statblock.tradition.always_has_focus:
            for i in range(len(aspects)):
                if "*" in aspects[i]:
                    aspects[i] = aspects[i].rstrip("*")
                    self.focus_aspects.append(aspects[i])

        self.aspects_box.configure(values=aspects)

    def check_focus_box(self):
        # show or hide foci box based on if the tradition always has a focus or if that particular aspect
        # has a focus
        if self.statblock.tradition is not None and \
                (self.statblock.tradition.always_has_focus or self.statblock.aspect in self.focus_aspects):
            self.focus_labelframe.grid(column=0, row=2, columnspan=3, sticky=N)
            self.rowconfigure(1, weight=1)  # to make the rows look nice and stack perfectly
            self.focus_box.configure(values=list(self.statblock.tradition.allowed_foci))
            self.focus_labelframe.configure(text=self.statblock.tradition.focus_name)
        else:
            self.focus_labelframe.grid_forget()

    def reload_data(self):
        # load traditions
        self.traditions_dict = {}
        try:
            tradition_data = app_data.game_data["Traditions"]
        except KeyError:
            tradition_data = {}

        for tradition in tradition_data:
            self.traditions_dict[tradition] = Tradition(tradition, **app_data.game_data["Traditions"][tradition])

        self.tradition_box.configure(values=list(self.traditions_dict.keys()))

        # load metamagic
        try:
            metamagic_data = app_data.game_data["Metamagic"]
        except KeyError:
            metamagic_data = {}

        for metamagic in metamagic_data:
            self.metamagic_library.append(Metamagic(name=metamagic, **metamagic_data[metamagic]))
            self.metamagic_listbox.insert(END, metamagic)

        # load ordeals
        try:
            ordeal_data = app_data.game_data["Ordeals"]
        except KeyError:
            ordeal_data = {}

        for ordeal in ordeal_data:
            self.ordeal_library.append(Ordeal(name=ordeal, **ordeal_data[ordeal]))
            self.ordeal_listbox.insert(END, ordeal)

    def calc_karma_cost(self):
        base_cost = 6 + self.statblock.grade

        if self.self_group_var.get() == "self":
            mult = 3.0
        elif self.self_group_var.get() == "group":
            mult = 2.0
        else:
            raise ValueError(f"Invalid self/group selection: {self.self_group_var.get()}")

        if self.ordeal_var.get():
            mult -= 0.5

        return int(base_cost * mult)

    def update_karma_cost(self):
        self.karma_cost_var.set(str(self.calc_karma_cost()))

    def load_character(self):
        if self.statblock.tradition is not None:
            self.fill_aspects()
            self.check_focus_box()

            self.tradition_box.set(self.statblock.tradition.name)
            if self.statblock.aspect is not None:
                self.aspects_box.set(self.statblock.aspect)
            if self.statblock.focus is not None:
                self.focus_box.set(self.statblock.focus)
        else:
            self.aspects_box.configure(values=[])
            self.focus_box.configure(values=[])

        self.geasa_listbox.delete(0, END)
        if len(self.statblock.geasa) > 0:
            self.geasa_listbox.insert(END, *self.statblock.geasa)

        self.geasa_listbox.delete(0, END)
        if len(self.statblock.magical_groups) > 0:
            self.group_listbox.insert(END, *self.statblock.magical_groups)

        self.initiations_listbox.delete(0, END)
        if len(self.statblock.initiations) > 0:
            self.initiations_listbox.insert(END, *self.statblock.initiations)

        self.on_switch()

    def on_switch(self):
        # show or hide aspects box
        if self.statblock.awakened == "Aspected":
            self.aspects_labelframe.grid(column=0, row=1, columnspan=3, sticky=N)
            self.rowconfigure(1, weight=9)  # to make the rows look nice and stack perfectly
        else:
            self.aspects_labelframe.grid_forget()

        self.update_karma_cost()
        self.check_focus_box()
