from abc import ABC
from tkinter import *
from tkinter import ttk

from src import app_data
from src.CharData.tradition import Tradition
from src.Tabs.notebook_tab import NotebookTab


class MagicBackgroundTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "MagicBackgroundTab")

        # the tradition box should be unchanging
        self.traditions_labelframe = ttk.LabelFrame(self, text="Tradition")
        self.tradition_box = ttk.Combobox(self.traditions_labelframe, state="readonly")
        self.tradition_box.bind("<<ComboboxSelected>>", self.on_change_tradition)
        self.tradition_box.grid(column=0, row=0)

        # setup and populate tradition _dict
        self.traditions_dict = None
        self.reload_data()

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
        self.geasa_listbox = Listbox(self.geasa_labelframe, width=40, height=7)
        self.geasa_scroll = Scrollbar(self.geasa_labelframe, orient="vertical", command=self.geasa_listbox.yview)
        self.geasa_listbox["yscrollcommand"] = self.geasa_scroll.set
        self.new_button = ttk.Button(self.geasa_labelframe, text="New")
        self.edit_button = ttk.Button(self.geasa_labelframe, text="Edit")
        self.delete_button = ttk.Button(self.geasa_labelframe, text="Delete")

        self.geasa_listbox.grid(column=0, row=0, rowspan=3)
        self.geasa_scroll.grid(column=1, row=0, rowspan=3, sticky=NS)
        self.new_button.grid(column=2, row=0, padx=5)
        self.edit_button.grid(column=2, row=1, padx=5)
        self.delete_button.grid(column=2, row=2, padx=5)

        # initiation stuff
        self.initiations_labelframe = ttk.LabelFrame(self, text="Initiations")
        self.initiations_listbox = Listbox(self.initiations_labelframe, height=10)

        # purchase options
        self.purchase_labelframe = ttk.LabelFrame(self.initiations_labelframe, text="New Initiation", width=6000)
        # self vs group initiation
        self.self_group_var = StringVar()
        self.self_radio = Radiobutton(self.purchase_labelframe, text="Self Initiation",
                                      variable=self.self_group_var, value="self")
        self.group_radio = Radiobutton(self.purchase_labelframe, text="Group Initiation",
                                       variable=self.self_group_var, value="group")

        # ordeal
        self.ordeal_var = IntVar()
        self.ordeal_checkbox = Checkbutton(self.purchase_labelframe, text="Ordeal", variable=self.ordeal_var)

        # karma cost label
        self.karma_cost_label = Label(self.purchase_labelframe, text="Karma Cost")
        self.karma_cost_var = StringVar()
        self.karma_cost_var.set("0")
        self.karma_cost_box = Entry(self.purchase_labelframe, textvariable=self.karma_cost_var, state="disabled",
                                    width=4)

        # buy button
        self.buy_button = Button(self.purchase_labelframe, text="Initiate")

        self.self_radio.grid(column=0, row=0, sticky=W)
        self.group_radio.grid(column=0, row=1, sticky=W)
        self.ordeal_checkbox.grid(column=0, row=2, sticky=W)
        self.karma_cost_label.grid(column=0, row=3, sticky=W)
        self.karma_cost_box.grid(column=1, row=3, sticky=W)
        self.buy_button.grid(column=0, row=4, sticky=W)

        # initiation benefit
        self.benefit_labelframe = ttk.LabelFrame(self.initiations_labelframe, text="Benefit")
        # radiobutton var
        self.benefit_var = StringVar()
        self.new_metamagic_button = Radiobutton(self.benefit_labelframe, text="Learn New Metamagic",
                                                variable=self.benefit_var, value="new_metamagic")
        self.alter_signature_button = Radiobutton(self.benefit_labelframe, text="Alter Astral Signature",
                                                  variable=self.benefit_var, value="alter_signature")
        self.shed_geas_button = Radiobutton(self.benefit_labelframe, text="Shed Geas",
                                            variable=self.benefit_var, value="shed_geas")

        self.new_metamagic_button.grid(column=0, row=0)
        self.alter_signature_button.grid(column=0, row=1)
        self.shed_geas_button.grid(column=0, row=2)

        # learn metamagic technique

        self.ordeal_labelframe = ttk.LabelFrame(self.initiations_labelframe, text="Ordeal")
        self.ordeal_listbox = Listbox(self.ordeal_labelframe, height=8)
        self.ordeal_scroll = Scrollbar(self.ordeal_labelframe, orient="vertical", command=self.ordeal_listbox.yview)
        self.ordeal_listbox["yscrollcommand"] = self.ordeal_scroll.set
        self.ordeal_listbox.grid(column=0, row=0)
        self.ordeal_scroll.grid(column=1, row=0, sticky=NS)

        self.metamagic_labelframe = ttk.LabelFrame(self.initiations_labelframe, text="Metamagic")
        self.metamagic_listbox = Listbox(self.metamagic_labelframe, height=8)
        self.metamagic_scroll = Scrollbar(self.metamagic_labelframe, orient="vertical",
                                          command=self.metamagic_listbox.yview)
        self.metamagic_listbox["yscrollcommand"] = self.metamagic_scroll.set
        self.metamagic_listbox.grid(column=0, row=0)
        self.metamagic_scroll.grid(column=1, row=0, sticky=NS)

        self.initiations_listbox.grid(column=0, row=0, columnspan=4, sticky=EW)

        self.purchase_labelframe.grid(column=0, row=1, sticky=NS)
        self.benefit_labelframe.grid(column=1, row=1, sticky=NS)
        self.ordeal_labelframe.grid(column=2, row=1, sticky=NS)
        self.metamagic_labelframe.grid(column=3, row=1, sticky=NS)

        # grids
        self.traditions_labelframe.grid(column=0, row=0, sticky=N)
        self.geasa_labelframe.grid(column=1, row=0, rowspan=10, sticky=EW)
        self.initiations_labelframe.grid(column=0, row=10, columnspan=2)

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
            self.focus_labelframe.grid(column=0, row=2, sticky="N")
            self.focus_box.configure(values=list(self.statblock.tradition.allowed_foci))
            self.focus_labelframe.configure(text=self.statblock.tradition.focus_name)
        else:
            self.focus_labelframe.grid_forget()

    def reload_data(self):
        self.traditions_dict = {}
        try:
            tradition_data = app_data.game_data["Traditions"]
        except KeyError:
            tradition_data = {}

        for tradition in tradition_data:
            self.traditions_dict[tradition] = Tradition(tradition, **app_data.game_data["Traditions"][tradition])

        self.tradition_box.configure(values=list(self.traditions_dict.keys()))

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

        self.on_switch()

    def on_switch(self):
        # show or hide aspects box
        if self.statblock.awakened == "Aspected":
            self.aspects_labelframe.grid(column=0, row=1, sticky="N")
        else:
            self.aspects_labelframe.grid_forget()

        self.check_focus_box()
