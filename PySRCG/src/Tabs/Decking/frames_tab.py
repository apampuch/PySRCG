import tkinter
from abc import ABC
from copy import deepcopy
from tkinter import *
from tkinter import ttk, messagebox
from typing import Literal, Any
from collections.abc import Callable

from src import app_data
from src.CharData.program import Program
from src.CharData.frameagent import FrameAgent
from src.GenModes.finalized import Finalized
from src.Tabs.notebook_tab import NotebookTab

from idlelib.tooltip import Hovertip


class LabelSpinbox:
    def __init__(self, parent, text, state: Literal["normal", "readonly", "disabled"] = "normal", from_=0, to=99):
        # super().__init__(parent)

        self.var = IntVar(master=parent)
        self.label = Label(parent, text=text)
        self.spinbox = Spinbox(parent, textvariable=self.var, state=state, width=2, increment=1, from_=from_, to=to)


class GridColumn:
    base_column: int
    grid_func: Callable[[Any, int], None]

    def __init__(self, base_column: int, grid_func: Callable[[Any, int], None]):
        self.base_column = base_column
        self.grid_row_count = 0
        self.grid_list = []
        self.grid_func = grid_func

    def append(self, v):
        self.grid_list.append(v)

    def grid_all(self):
        for item in self.grid_list:
            self.grid_row(item)

    def grid_row(self, obj):
        if type(obj) == LabelSpinbox:
            obj.label.grid(column=self.base_column, row=self.grid_row_count, sticky=W)
            obj.spinbox.grid(column=self.base_column + 1, row=self.grid_row_count, sticky=E)
        elif type(obj) == LabelFrame:
            obj.grid(column=self.base_column, row=self.grid_row_count, sticky=EW, columnspan=2, rowspan=2)
            self.grid_row_count += 1
        else:
            obj.grid(column=self.base_column, row=self.grid_row_count, sticky=EW, columnspan=2)
        self.grid_row_count += 1


class FramesTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "FramesTab")

        # function to pass into all gridcolumns
        def grid_func(obj, count):
            if type(obj) == LabelSpinbox:
                obj.label.grid(column=0, row=count, sticky=W)
                obj.spinbox.grid(column=1, row=count, sticky=E)
            else:
                obj.grid(column=0, row=count, sticky=W)

        self.main_grid = GridColumn(0, grid_func)
        self.persona_grid = GridColumn(2, grid_func)
        self.frame_grid = GridColumn(4, grid_func)

        # name entry
        self.name_var = StringVar()
        self.name_label = LabelFrame(self, text="Frame Name")
        self.name_entry = ttk.Entry(self.name_label, textvariable=self.name_var)
        self.name_entry.pack(padx=4, pady=4, fill=X)
        self.main_grid.append(self.name_label)

        # dropdown for frame type
        self.frame_type_var = StringVar()
        self.frame_label = LabelFrame(self, text="Frame Type")
        self.frame_type_combobox = ttk.Combobox(self.frame_label, textvariable=self.frame_type_var,
                                                values=("Dumb", "Smart", "Agent"), state="readonly")
        self.frame_type_combobox.bind("<<ComboboxSelected>>", self.on_select_type)
        self.frame_type_combobox.set("Dumb")
        self.frame_type_combobox.pack(padx=4, pady=4)
        self.main_grid.append(self.frame_label)

        # spinbox for frame rating
        self.core_rating = LabelSpinbox(self, "Core Rating")
        self.core_rating.var.trace_add("write", self.on_adjust_core_rating)
        self.main_grid.append(self.core_rating)

        # unusable spinbox for persona points
        self.persona_points = LabelSpinbox(self, "Persona Points", "disabled")
        self.persona_grid.append(self.persona_points)

        # spinboxes for bod/evasion/etc
        self.bod = LabelSpinbox(self, "Bod")
        self.bod.var.trace_add("write", self.on_adjust_core_attribute)
        self.evasion = LabelSpinbox(self, "Evasion")
        self.evasion.var.trace_add("write", self.on_adjust_core_attribute)
        self.masking = LabelSpinbox(self, "Masking")
        self.masking.var.trace_add("write", self.on_adjust_core_attribute)
        self.sensor = LabelSpinbox(self, "Sensor")
        self.sensor.var.trace_add("write", self.on_adjust_core_attribute)

        self.persona_grid.append(self.bod)
        self.persona_grid.append(self.evasion)
        self.persona_grid.append(self.masking)
        self.persona_grid.append(self.sensor)

        # unusable spinbox for frame points
        self.frame_points = LabelSpinbox(self, "Frame Points", "disabled")
        self.frame_grid.append(self.frame_points)

        # spinboxes for reaction/init/hacking pool/payload/pilot
        self.initiative = LabelSpinbox(self, "Initiative")
        self.initiative.var.trace_add("write", self.on_adjust_frame_attribute)
        self.payload = LabelSpinbox(self, "Utility Payload")
        self.payload.var.trace_add("write", self.on_adjust_frame_attribute)
        self.pilot = LabelSpinbox(self, "Pilot Rating")
        self.pilot.var.trace_add("write", self.on_adjust_frame_attribute)

        self.frame_grid.append(self.initiative)
        self.frame_grid.append(self.payload)
        self.frame_grid.append(self.pilot)

        # shitty library for utlities
        self.library_list = []
        self.utilities_library = LabelFrame(self, text="All Utilities")
        self.utilities_library_listbox = Listbox(self.utilities_library, selectmode=EXTENDED)
        self.utilities_library_listbox.pack(padx=4, pady=4)

        # shitty list for utilities
        self.utilities_list = []
        self.utilities_container = LabelFrame(self, text="Utility Programs")
        self.utilities_listbox = Listbox(self.utilities_container, selectmode=EXTENDED)
        self.utilities_listbox.pack(padx=4, pady=4)

        # button to add utility
        self.add_utility_button = Button(self, text="Add", command=self.on_add_click)

        # spinbox to determine grade
        self.grade_label = Label(self, text="Rating:")
        self.utility_rating_spinbox = Spinbox(self, width=2, from_=1, to=99, increment=1)

        # button to remove utility
        self.remove_utility_button = Button(self, text="Remove", command=self.on_remove_click)

        # checkbox to pay cash (always checked unless finalized)
        self.cash_var = BooleanVar()
        self.cash_checkbox = ttk.Checkbutton(self, variable=self.cash_var, text="Pay Cash",
                                             command=self.update_cost_and_mp)
        self.cash_tip = Hovertip(self.cash_checkbox,
                                 "This should probably be checked if you're programming it yourself.\n"
                                 "It could be unchcked to add in a frame you got for free somehow,\n"
                                 "such as through theft.")
        self.main_grid.append(self.cash_checkbox)

        # checkbox to use own skill
        self.self_programming_var = BooleanVar()
        self.self_programming_checkbox = ttk.Checkbutton(self, variable=self.self_programming_var,
                                                         text="Self-Programmed",
                                                         command=self.on_self_programmed_toggle)
        self.self_programming_tip = Hovertip(self.self_programming_checkbox,
                                             "Check this if you're programming the frame yourself.\n"
                                             "This will limit the rating of the frame, and limit the\n"
                                             "utilities to those available to you.\n"
                                             "The price of these utilities won't be added to the nuyen cost.")
        self.main_grid.append(self.self_programming_checkbox)

        self.build_button = Button(self, text="Build Frame", command=self.on_build_click)
        self.main_grid.append(self.build_button)

        self.cost_label = Label(self, text="Cost: ¥0")
        self.mp_label = Label(self, text="Mp: 0")

        self.main_grid.grid_all()
        self.persona_grid.grid_all()
        self.frame_grid.grid_all()

        self.utilities_library.grid(column=6, row=0, columnspan=2, rowspan=6)
        self.utilities_container.grid(column=8, row=0, columnspan=2, rowspan=6)

        self.add_utility_button.grid(column=6, row=6, sticky=W)
        self.grade_label.grid(column=7, row=6, sticky=E, padx=2)
        self.utility_rating_spinbox.grid(column=8, row=6, sticky=W, padx=2)
        self.remove_utility_button.grid(column=9, row=6, sticky=E)

        # do this separate so it's lined up with button
        self.cost_label.grid(column=2, row=self.main_grid.grid_row_count - 1)
        self.mp_label.grid(column=4, row=self.main_grid.grid_row_count - 1)

    def get_mults(self):
        frame_type = self.frame_type_combobox.get()
        if frame_type == "Dumb":
            core_mult = 2
            persona_mult = 1
            frame_mult = 2
            size_mult = 3
        elif frame_type == "Smart":
            core_mult = 1.5
            persona_mult = 1
            frame_mult = 4
            size_mult = 6
        elif frame_type == "Agent":
            core_mult = 1
            persona_mult = 2
            frame_mult = 6
            size_mult = 10
        else:
            raise ValueError(f"{frame_type} not valid type of frame.")

        return core_mult, persona_mult, frame_mult, size_mult

    def update_cost_and_mp(self):
        rating = self.core_rating.var.get()
        size = rating * rating * self.get_mults()[3]
        if not self.cash_var.get():
            cost = 0
        elif rating < 4:
            cost = 100 * size
        elif 4 <= rating < 7:
            cost = 200 * size
        elif 7 <= rating < 10:
            cost = 500 * size
        else:
            cost = 1000 * size

        # include costs of programs if not programming it
        if self.cash_var.get() and not self.self_programming_var.get():
            cost += sum(map(lambda x: x.properties["cost"], self.utilities_list))

        mp = size + sum(map(lambda x: x.properties["size"], self.utilities_list))

        self.cost_label.config(text=f"Cost: ¥{cost}")
        self.mp_label.config(text=f"Mp: {mp}")

    def on_select_type(self, event):
        # matrix, p89
        if not self.self_programming_var.get():
            self.core_rating.spinbox.config(to=99)
        else:
            # get type of frame and set multipliers
            core_mult = self.get_mults()[0]

            # set frame core rating max
            self.core_rating.spinbox.config(to=int(self.statblock.skill_or_specialization_rank
                                                   ("Computer", "Programming") * core_mult))
            self.core_rating.var.set(min(self.core_rating.var.get(), self.statblock.skill_or_specialization_rank
                                     ("Computer", "Programming")))

        if self.frame_type_var.get() == "Dumb":
            self.pilot.var.set(0)
            self.initiative.var.set(0)
            self.pilot.spinbox.config(state="disabled")
            self.initiative.spinbox.config(state="disabled")
            self.on_adjust_frame_attribute()
        else:
            self.pilot.spinbox.config(state="normal")
            self.initiative.spinbox.config(state="normal")

        self.on_adjust_core_rating(None, None, "write")

    def on_adjust_core_rating(self, *args):
        self.on_adjust_core_attribute(args)
        self.on_adjust_frame_attribute(args)
        self.update_cost_and_mp()

    def on_adjust_core_attribute(self, *args):
        core_val = self.core_rating.var.get()

        persona_mult = self.get_mults()[1]

        # set persona points
        persona_max = core_val * persona_mult
        persona_val = persona_max

        # subtract already assigned persona attributes
        persona_val -= self.bod.var.get()
        persona_val -= self.evasion.var.get()
        persona_val -= self.masking.var.get()
        persona_val -= self.sensor.var.get()

        self.persona_points.spinbox.config(to=persona_max)

        # if negative, reset everything to 0
        if persona_val < 0:
            persona_val = persona_max
            self.persona_points.var.set(persona_max)
            self.bod.var.set(0)
            self.evasion.var.set(0)
            self.masking.var.set(0)
            self.sensor.var.set(0)

        self.persona_points.var.set(persona_val)

        self.bod.spinbox.config(to=self.bod.var.get() + persona_val)
        self.evasion.spinbox.config(to=self.evasion.var.get() + persona_val)
        self.masking.spinbox.config(to=self.masking.var.get() + persona_val)
        self.sensor.spinbox.config(to=self.sensor.var.get() + persona_val)

    def on_adjust_frame_attribute(self, *args):
        core_val = self.core_rating.var.get()

        frame_mult = self.get_mults()[2]

        # set persona points
        frame_max = core_val * frame_mult
        frame_val = frame_max

        # subtract already assigned persona attributes
        frame_val -= self.initiative.var.get() * 3
        frame_val -= self.payload.var.get()
        frame_val -= self.pilot.var.get() * 2

        self.frame_points.spinbox.config(to=frame_max)

        # if negative, reset everything to 0
        if frame_val < 0:
            frame_val = frame_max
            self.frame_points.var.set(frame_max)
            self.initiative.var.set(0)
            self.payload.var.set(0)
            self.pilot.var.set(0)

        self.frame_points.var.set(frame_val)

        self.initiative.spinbox.config(to=self.initiative.var.get() + (frame_val // 3))
        self.payload.spinbox.config(to=self.payload.var.get() + frame_val)
        self.pilot.spinbox.config(to=self.pilot.var.get() + (frame_val // 2))

    def fill_library(self):
        self.library_list.clear()
        self.utilities_library_listbox.delete(0, END)

        # fill with just what we have if self-programming
        if self.self_programming_var.get():
            all_memory_stuff = self.statblock.inventory + self.statblock.cyberware + self.statblock.cyberware + \
                               self.statblock.decks

            all_memory_stuff = filter(lambda x: "stored_memory" in x.properties, all_memory_stuff)
            all_memory_stuff = sum(map(lambda x: x.properties["stored_memory"], all_memory_stuff), start=[])
            all_memory_stuff += self.statblock.other_programs

            self.library_list = all_memory_stuff
            for program in self.library_list:
                self.utilities_library_listbox.insert(END, f"{program.name} [{program.properties['rating']}]")

        # otherwise fill with every utility available
        else:
            for category_key in app_data.game_data["Programs"]:
                for program in app_data.game_data["Programs"][category_key]:
                    p_data = app_data.game_data["Programs"][category_key][program]
                    self.library_list.append(Program(name=program, **p_data))

            self.library_list.sort(key=lambda x: x.name.lower())
            for program in self.library_list:
                self.utilities_library_listbox.insert(END, program.name)

    def on_add_click(self):
        selection_range = self.utilities_library_listbox.curselection()

        # check for valid utility rating
        if not self.self_programming_var.get():
            try:
                rating = int(self.utility_rating_spinbox.get())
            except ValueError:
                print("Not a valid rating!")
                return
            # validate that we have enough utility payload
            selected_payload = rating * len(selection_range)
        else:
            # get programs from indices
            ratings = map(lambda x: self.library_list[x].properties["rating"], selection_range)
            selected_payload = sum(ratings)
            print(selected_payload)

        if sum(map(lambda x: x.properties["rating"], self.utilities_list)) + selected_payload > \
                self.payload.var.get():
            print("Too much payload!")
            return

        for index in selection_range:
            utility = deepcopy(self.library_list[index])

            # add rating if brand new
            if not self.self_programming_var.get():
                utility.properties["rating"] = rating

            name = f"{utility.name} [{utility.properties['rating']}]"

            self.utilities_listbox.insert(END, name)
            self.utilities_list.append(utility)

        self.update_cost_and_mp()

    def on_remove_click(self):
        selection_range = self.utilities_listbox.curselection()

        for index in selection_range:
            self.utilities_list[index] = None

        self.utilities_list = list(filter(lambda x: x is not None, self.utilities_list))
        self.utilities_listbox.delete(0, END)
        for utility in self.utilities_list:
            name = f"{utility.name} [{utility.properties['rating']}]"
            self.utilities_listbox.insert(END, name)

        self.update_cost_and_mp()

    def on_build_click(self):
        # validate that it has a name
        if self.name_var.get() == "" or str.isspace(self.name_var.get()):
            print("Need a name!")
            return
        # validate that some values aren't zero
        if self.core_rating.var.get() <= 0:
            print("Need a core rating higher than 0!")
        # throw a warning if build points are greater than zero
        if self.persona_points.var.get() > 0 or self.frame_points.var.get() > 0:
            if not messagebox.askyesno("Confirm", "Not all build points are spent, are you sure you wish "
                                                  "to build this frame?"):
                return

        # calculate size
        frame = FrameAgent(name=self.name_var.get(),
                           rating=self.core_rating.var.get(),
                           multiplier=self.get_mults()[3],
                           bod=self.bod.var.get(),
                           evasion=self.evasion.var.get(),
                           sensor=self.evasion.var.get(),
                           masking=self.masking.var.get(),
                           frame_type=self.frame_type_var.get(),
                           utility_payload=self.payload.var.get(),
                           utilities=self.utilities_list,
                           initiative=self.initiative.var.get(),
                           pilot_rating=self.pilot.var.get(),
                           book="Matrix (FAS7909)",
                           page=88)
        # make new list for utilities list so that we don't keep referencing the same one
        self.utilities_list = []
        self.utilities_listbox.delete(0, END)

        # validate that we have enough cash if paying cash
        if self.cash_var.get():
            paid = app_data.pay_cash(frame.cost())
        else:
            paid = True

        if paid:
            self.statblock.other_programs.append(frame)
            self.core_rating.var.set(0)
            self.name_var.set("")

    def on_self_programmed_toggle(self):
        if self.self_programming_var.get():
            self.cash_var.set(False)
            self.cash_checkbox.config(state=DISABLED)
        else:
            self.cash_checkbox.config(state=NORMAL)

        self.fill_library()
        self.on_select_type(None)

    def on_switch(self):
        super().on_switch()
        self.on_select_type(None)
        self.on_adjust_core_rating(None, None, None)

        # force self programming off and pay cash on if we're not finalized, so we can't generate infinite money
        if type(self.statblock.gen_mode) is not Finalized:
            self.self_programming_var.set(False)
            self.self_programming_checkbox.config(state=DISABLED)
            self.cash_var.set(False)
            self.cash_checkbox.config(state=DISABLED)
        else:
            self.self_programming_checkbox.config(state=NORMAL)
            self.cash_checkbox.config(state=NORMAL)

        # add all
        self.fill_library()

    def load_character(self):
        super().load_character()
        self.on_switch()
