from abc import ABC
from math import ceil
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Combobox

from src.Tabs.notebook_tab import NotebookTab


# should be hidden if character is not an otaku
class OtakuTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "OtakuTab")
        self.living_persona_frame = ttk.Labelframe(self, text="Living Persona")

        self.mpcp_label = Label(self.living_persona_frame, text="0")
        self.bod_label = Label(self.living_persona_frame, text="0")
        self.evasion_label = Label(self.living_persona_frame, text="0")
        self.masking_label = Label(self.living_persona_frame, text="0")
        self.sensor_label = Label(self.living_persona_frame, text="0")
        self.reaction_label = Label(self.living_persona_frame, text="0")
        self.initiative_label = Label(self.living_persona_frame, text="0")
        self.hardening_label = Label(self.living_persona_frame, text="0")
        self.io_speed_label = Label(self.living_persona_frame, text="0")

        # only show this when not finalized
        self.channels_label = Label(self, text="Free Channels: ")

        # otaku path
        path_frame = ttk.LabelFrame(self, text="Path")
        self.path_var = StringVar()
        self.path_combobox = Combobox(path_frame, values=("Cyberadept", "Technoshaman"), state="readonly",
                                      textvariable=self.path_var)
        self.path_combobox.bind("<<ComboboxSelected>>", self.on_path_selected)

        # grids
        self.living_persona_frame.grid(column=0, row=0)
        self.channels_label.grid(column=0, row=1)

        Label(self.living_persona_frame, text="MPCP").grid(column=0, row=0, sticky=W, padx=8, pady=2)
        Label(self.living_persona_frame, text="Bod").grid(column=0, row=1, sticky=W, padx=8, pady=2)
        Label(self.living_persona_frame, text="Evasion").grid(column=0, row=2, sticky=W, padx=8, pady=2)
        Label(self.living_persona_frame, text="Masking").grid(column=0, row=3, sticky=W, padx=8, pady=2)
        Label(self.living_persona_frame, text="Sensor").grid(column=0, row=4, sticky=W, padx=8, pady=2)
        Label(self.living_persona_frame, text="Matrix Reaction").grid(column=0, row=5, sticky=W, padx=8, pady=2)
        Label(self.living_persona_frame, text="Matrix Initiative").grid(column=0, row=6, sticky=W, padx=8, pady=2)
        Label(self.living_persona_frame, text="Hardening").grid(column=0, row=7, sticky=W, padx=8, pady=2)
        Label(self.living_persona_frame, text="I/O Speed").grid(column=0, row=8, sticky=W, padx=8, pady=2)

        self.mpcp_label.grid(column=1, row=0, sticky=W, padx=8, pady=2)
        self.bod_label.grid(column=1, row=1, sticky=W, padx=8, pady=2)
        self.evasion_label.grid(column=1, row=2, sticky=W, padx=8, pady=2)
        self.masking_label.grid(column=1, row=3, sticky=W, padx=8, pady=2)
        self.sensor_label.grid(column=1, row=4, sticky=W, padx=8, pady=2)
        self.reaction_label.grid(column=1, row=5, sticky=W, padx=8, pady=2)
        self.initiative_label.grid(column=1, row=6, sticky=W, padx=8, pady=2)
        self.hardening_label.grid(column=1, row=7, sticky=W, padx=8, pady=2)
        self.io_speed_label.grid(column=1, row=8, sticky=W, padx=8, pady=2)

        path_frame.grid(column=1, row=0, sticky=N)
        self.path_combobox.pack()

    def on_path_selected(self, event):
        selected_path = event.widget.get()
        self.statblock.otaku_path = selected_path

    def calculate_persona(self):
        s = self.statblock
        self.mpcp_label.config(text=ceil((s.intelligence + s.willpower + s.charisma) / 3))
        self.bod_label.config(text=s.willpower)
        self.evasion_label.config(text=s.intelligence)
        self.masking_label.config(text=ceil((s.willpower + s.charisma) / 2))
        self.sensor_label.config(text=s.intelligence)
        self.reaction_label.config(text=s.intelligence)  # TODO include other stuff that might boost this
        self.initiative_label.config(text=f"4d6 + {s.intelligence}")  # TODO include other stuff that might boost this
        self.hardening_label.config(text=ceil(s.willpower / 2))
        self.io_speed_label.config(text=f"{s.intelligence * 100} Mp")
        self.channels_label.config(text=f"Free Channels: {ceil((s.intelligence + s.willpower + s.charisma) / 3)}")

    def reload_data(self):
        pass

    def on_switch(self):
        self.calculate_persona()

    def load_character(self):
        self.path_var.set(self.statblock.otaku_path)
        self.on_switch()
