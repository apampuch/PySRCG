from abc import ABC
from tkinter import *
from tkinter import ttk

from src import app_data
from src.CharData.augment import Cyberware
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
        super().__init__(parent, "SetupTab")
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

        # generation options
        self.gen_frame = ttk.LabelFrame(self, text="Generation Mode")
        self.gen_mode_frame = Frame(self.gen_frame)
        GenMode.gen_mode_frame = self.gen_mode_frame
        self.gen_modes = (Priority, Points)
        self.gen_mode_index = IntVar()

        self.priority_gen_radio = Radiobutton(self.gen_frame, text="Priority", variable=self.gen_mode_index, value=0)
        self.points_gen_radio = Radiobutton(self.gen_frame, text="Points",
                                            variable=self.gen_mode_index, value=1, state=DISABLED)

        self.otaku_var = BooleanVar()  # doesn't do anything on its own, only used to make things saner
        self.otaku_checkbox = Checkbutton(self, text="Otaku Character", variable=self.otaku_var,
                                          command=self.on_otaku_checked)

        # can only be checked while otaku
        # this limits all physical attributes to 1 but increases mental limits by 2
        self.runt_var = BooleanVar()
        self.runt_checkbox = Checkbutton(self, text="Runt Otaku", variable=self.runt_var,
                                         command=self.on_runt_checked, state="disabled")

        # grids
        self.gen_frame.grid(column=0, row=0, columnspan=3)
        self.gen_mode_frame.grid(column=0, row=1, columnspan=5)
        self.priority_gen_radio.grid(column=0, row=0)
        self.points_gen_radio.grid(column=1, row=0)

        self.race_box.grid(column=5, row=0)

        self.otaku_checkbox.grid(column=0, row=1, sticky=W)
        self.runt_checkbox.grid(column=1, row=1, sticky=W)

        self.priority_gen_radio.select()

    def on_otaku_checked(self):
        self.character.statblock.otaku = self.otaku_var.get()

        # fix runt otaku checkbox
        if self.otaku_var.get():
            # undo everything if we can't set otaku
            success = self.gen_mode.on_set_otaku()
            if not success:
                self.otaku_var.set(False)
                self.character.statblock.otaku = False
                return
            self.runt_checkbox.config(state="active")
        else:
            success = self.gen_mode.on_unset_otaku()
            # undo everything if we can't unset otaku
            if not success:
                self.otaku_var.set(True)
                self.character.statblock.otaku = True
            self.runt_checkbox.config(state="disabled")
            self.runt_var.set(False)
            self.statblock.runt_otaku = False

        if self.otaku_var.get():
            # make datajack and asist converter objects
            datajack = Cyberware(name="Otaku Datajack", **app_data.game_data["Cyberware"]["Headware"]["Datajack"])
            datajack.properties["unsellable"] = True

            asist_converter = Cyberware(name="Otaku ASIST Converter", **app_data.game_data["Cyberware"]
                                        ["Brainware"]["ASIST Converter (datajack accessory)"])
            asist_converter.properties["unsellable"] = True

            # give free (unsellable?) datajack and ASIST converter
            self.statblock.cyberware.append(datajack)
            self.statblock.cyberware.append(asist_converter)

            # turn on skill/attribute requirements/limits

            # enable channels/complex form/echo tabs
            # disable normal decking tabs
            pass
        else:
            # force awakened on or move magic somewhere else
            # take back free datajack and ASIST converter
            c: Cyberware
            datajack, asist_converter = None, None
            for c in self.statblock.cyberware:
                if "unsellable" in c.properties:
                    if c.name == "Otaku Datajack":
                        datajack = c
                    elif c.name == "Otaku ASIST Converter":
                        asist_converter = c

            if datajack is None or asist_converter is None:
                print("OTAKU IS MISSING AUGMENTS")
                # reset otaku checkbox status
                return

            self.statblock.cyberware.remove(datajack)
            self.statblock.cyberware.remove(asist_converter)

            # turn off skill/attribute requirements/limits

            # disable channels/complex form/echo tabs
            # enable normal decking tabs
            pass

    def on_runt_checked(self):
        self.statblock.runt_otaku = self.runt_var.get()

    def on_race_selected(self, event):
        """Event to set the race of the current character."""
        selected_race = event.widget.get()
        self.race = all_races[selected_race]

    def load_character(self):
        self.otaku_var.set(self.statblock.otaku)
        self.runt_var.set(self.statblock.runt_otaku)
        if self.statblock.runt_otaku:
            self.runt_checkbox.config(state="normal")
        else:
            self.runt_checkbox.config(state="disabled")
        self.on_switch()

    def on_switch(self):
        race_name = self.race.name
        race_index = self.race_vals.index(race_name)
        self.race_box.current(race_index)
