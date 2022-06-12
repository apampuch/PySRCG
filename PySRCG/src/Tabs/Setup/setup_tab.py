from abc import ABC
from tkinter import *
from tkinter import ttk
from src.CharData.race import all_races
from src.GenModes.gen_mode import GenMode
from src.GenModes.points import Points
from src.GenModes.priority import Priority
from src.Tabs.notebook_tab import NotebookTab


class SetupTab(NotebookTab, ABC):
    @NotebookTab.race.setter
    def race(self, value):
        self.statblock.race = value

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # TODO move this to SR3_Core and make it take from there
        self.race_vals = ["Human",
                          "Dwarf",
                          "Elf",
                          "Ork",
                          "Troll"]

        self.race_box = ttk.Combobox(self, values=self.race_vals, state="readonly")
        self.race_box.bind("<<ComboboxSelected>>", self.on_race_selected)
        self.race_box.current(0)
        # self.character.statblock.race = all_races[self.race_vals[0]]

        # self.magic_frame = ttk.LabelFrame(self, text="Magic User?")

        # self.magic_var = StringVar()
        # self.magic_none_radio = Radiobutton(self.magic_frame, text="None", variable=self.magic_var, value="none")
        # self.magic_full_radio = Radiobutton(self.magic_frame, text="Full", variable=self.magic_var, value="full")
        # self.magic_aspected_radio = Radiobutton(self.magic_frame, text="Aspected", variable=self.magic_var, value="aspected")

        # generation options
        self.gen_frame = ttk.LabelFrame(self, text="Generation Mode")
        self.gen_mode_frame = Frame(self.gen_frame)
        GenMode.gen_mode_frame = self.gen_mode_frame
        self.gen_modes = (Priority, Points)
        self.gen_mode_index = IntVar()

        self.priority_gen_radio = Radiobutton(self.gen_frame, text="Priority", variable=self.gen_mode_index, value=0)
        self.points_gen_radio = Radiobutton(self.gen_frame, text="Points", variable=self.gen_mode_index, value=1, state=DISABLED)

        # grids
        self.gen_frame.grid(column=0, row=0)
        self.gen_mode_frame.grid(column=0, row=1, columnspan=5)
        self.priority_gen_radio.grid(column=0, row=0)
        self.points_gen_radio.grid(column=1, row=0)

        self.race_box.grid(column=5, row=0)

        self.priority_gen_radio.select()

    def on_race_selected(self, event):
        """Event to set the race of the current character."""
        selected_race = event.widget.get()
        self.race = all_races[selected_race]

    def load_character(self):
        self.on_switch()

    def on_switch(self):
        race_name = self.race.name
        race_index = self.race_vals.index(race_name)
        self.race_box.current(race_index)
