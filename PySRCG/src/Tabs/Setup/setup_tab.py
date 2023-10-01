from abc import ABC
from tkinter import *
from tkinter import ttk

from src import app_data
from src.CharData.augment import Cyberware
from src.CharData.metatype import Metatype
from src.GenModes.gen_mode import GenMode
from src.GenModes.points import Points
from src.GenModes.priority import Priority
from src.Tabs.notebook_tab import NotebookTab


class SetupTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "SetupTab")
        self.parent = parent

        # TODO move this to SR3_Core and make it take from there
        self.metatype_vals = ["Human",
                              "Dwarf",
                              "Elf",
                              "Ork",
                              "Troll"]

        self.metatype_box = ttk.Combobox(self, values=self.metatype_vals, state="readonly")
        self.metatype_box.bind("<<ComboboxSelected>>", self.on_metatype_selected)
        self.metatype_box.current(0)

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

        self.metatype_box.grid(column=5, row=0)

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

    def on_metatype_selected(self, event):
        """Event to set the metatype of the current character."""
        selected_metatype = event.widget.get()
        metatype = app_data.game_data["Metatypes"][selected_metatype]
        self.statblock.metatype = Metatype(selected_metatype, **metatype)

    def load_character(self):
        self.otaku_var.set(self.statblock.otaku)
        self.runt_var.set(self.statblock.runt_otaku)
        if self.statblock.runt_otaku:
            self.runt_checkbox.config(state="normal")
        else:
            self.runt_checkbox.config(state="disabled")
        self.on_switch()

    def on_switch(self):
        metatype_name = self.statblock.metatype.name
        metatype_index = self.metatype_vals.index(metatype_name)
        self.metatype_box.current(metatype_index)
