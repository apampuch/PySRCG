from abc import ABC
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

        self.traditions_labelframe.grid(column=0, row=0)

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
            self.focus_labelframe.grid(column=0, row=2)
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
            self.aspects_labelframe.grid(column=0, row=1)
        else:
            self.aspects_labelframe.grid_forget()

        self.check_focus_box()
