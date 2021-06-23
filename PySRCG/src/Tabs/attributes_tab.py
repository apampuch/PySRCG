from src import app_data
from src.GenModes.finalized import Finalized
from src.Tabs.notebook_tab import NotebookTab
from tkinter import *
from tkinter import ttk
from typing import Dict

from src.adjustment import Adjustment
from src.statblock_modifier import StatMod


class AttributesTab(NotebookTab):
    sliders: Dict[str, Scale]
    slider_vars: Dict[str, IntVar]
    # slider_absolute_vars: Dict[str, int]
    attribute_labels: Dict[str, ttk.Label]
    mod_labels: Dict[str, Dict[str, ttk.Label]]

    base_attributes = ["body", "quickness", "strength", "charisma", "intelligence", "willpower"]
    derived_attributes = ["essence", "magic", "reaction", "initiative"]

    def __init__(self, parent):
        super().__init__(parent)

        self.minus_buttons = {}
        self.plus_buttons = {}
        # self.bullshit_count = 0 # scream test to delete this

        self.sliders = {}
        self.slider_vars = {}
        self.slider_old_vals = {}
        self.attribute_labels = {}
        self.mod_labels = {
            "slider": {},
            "race": {},
            "bio": {},
            "cyber": {},
            "other": {},
            "total": {}
        }

        self.current_row = 0

        # place labels, actual labels, not ttk labels

        self.race_label = ttk.Label(self, text="Attribute", padding=5)
        self.race_label.grid(column=0, row=self.current_row)

        # leave slider space blank
        self.blank_space = ttk.Label(self, text="Slider", padding=5)
        self.blank_space.grid(column=1, columnspan=2, row=self.current_row)

        self.race_mod_label = ttk.Label(self, text="Race", padding=5)
        self.race_mod_label.grid(column=3, row=self.current_row)

        self.bio_mod_label = ttk.Label(self, text="Bio", padding=5)
        self.bio_mod_label.grid(column=4, row=self.current_row)

        self.cyber_mod_label = ttk.Label(self, text="Cyber", padding=5)
        self.cyber_mod_label.grid(column=5, row=self.current_row)

        self.other_mod_label = ttk.Label(self, text="Other", padding=5)
        self.other_mod_label.grid(column=6, row=self.current_row)

        self.total_label = ttk.Label(self, text="Total", padding=5)
        self.total_label.grid(column=7, row=self.current_row)

        self.current_row += 1

        # setup the grid of shit
        for attr in AttributesTab.base_attributes:
            self.setup_slider_and_label(attr)

        for attr in AttributesTab.derived_attributes:
            self.setup_slider_and_label(attr, True)

        # override reaction command because reaction is special
        # self.sliders["reaction"].configure(command=lambda x: self.on_set_reaction_value(x))

        ###################
        # DICE POOL STUFF #
        ###################

        # style for red text
        red_text_style = ttk.Style()
        red_text_style.configure("Red.TLabel", foreground="red")

        # dice pool variables
        self.combat_pool_val = StringVar()
        self.control_pool_val = StringVar()
        self.hacking_pool_val = StringVar()
        self.spell_pool_val = StringVar()
        self.task_pool_val = StringVar()
        self.astral_combat_pool_val = StringVar()

        # set dice pool values
        self.set_pool_vals()

        # dice pool labels
        self.dice_pool_labelframe = ttk.LabelFrame(self, text="Dice Pools")
        self.dice_pool_labelframe.grid(column=8, row=1, rowspan=5)

        self.combat_pool_label = ttk.Label(self.dice_pool_labelframe, text="Combat: ")
        self.combat_pool_label.grid(column=0, row=0)

        self.control_pool_label = ttk.Label(self.dice_pool_labelframe, text="Control: ")
        self.control_pool_label.grid(column=0, row=1)

        self.hacking_pool_label = ttk.Label(self.dice_pool_labelframe, text="Hacking: ")
        self.hacking_pool_label.grid(column=0, row=2)

        self.spell_pool_label = ttk.Label(self.dice_pool_labelframe, text="Spell: ")
        self.spell_pool_label.grid(column=0, row=3)

        self.task_pool_label = ttk.Label(self.dice_pool_labelframe, text="Task: ")
        self.task_pool_label.grid(column=0, row=4)

        self.astral_combat_pool_label = ttk.Label(self.dice_pool_labelframe, text="Astral Combat: ")
        self.astral_combat_pool_label.grid(column=0, row=5)

        # dice pool value labels
        self.combat_pool_val_label = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvar=self.combat_pool_val
        )
        self.combat_pool_val_label.grid(column=1, row=0)

        self.control_pool_val_label = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvar=self.control_pool_val
        )
        self.control_pool_val_label.grid(column=1, row=1)

        self.hacking_pool_val_label = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvar=self.hacking_pool_val
        )
        self.hacking_pool_val_label.grid(column=1, row=2)

        self.spell_pool_val_label = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvar=self.spell_pool_val
        )
        self.spell_pool_val_label.grid(column=1, row=3)

        self.task_pool_val_label = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvar=self.task_pool_val
        )
        self.task_pool_val_label.grid(column=1, row=4)

        self.astral_combat_pool_label_labelframe = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvar=self.astral_combat_pool_val
        )
        self.astral_combat_pool_label_labelframe.grid(column=1, row=5)

        # setup the other attributes
        self.sliders["essence"].set(6)

    def setup_slider_and_label(self, key, other_attribute=False):
        """Initial setup. Should only be run once per attribute."""
        self.slider_vars[key] = IntVar()             # this is the internal variable
        self.slider_vars[key].set(1)                 # initialize it to 1
        self.slider_old_vals[key] = IntVar()         # this is to correct for when we try to go over our total
        self.slider_old_vals[key].set(1)             # initialize it to 1

        # setup the ui elements

        # this is the label for the attribute itself
        # self.attribute_labels[key] = ttk.Label(self, text=key.capitalize())
        self.attribute_labels[key] = ttk.Label(self, text=key.capitalize())

        # on switch, make a slider if gen mode is anything other than finalized
        # otherwise add a + and - button

        # container frame for either our slider or our buttons
        adjustment_container_frame = Frame(self)

        # the slider itself
        if other_attribute:
            racial_slider_minimum = 0
        else:
            racial_slider_minimum = self.race.racial_slider_minimum(key)

        self.sliders[key] = Scale(adjustment_container_frame,
                                  from_=racial_slider_minimum, to=6,
                                  variable=self.slider_vars[key],
                                  command=lambda x: self.on_set_attribute_value(key, x),
                                  orient=HORIZONTAL, showvalue=0)

        # - and + buttons if we're finalized
        self.minus_buttons[key] = Button(adjustment_container_frame,
                                         text="-",
                                         command=lambda: self.minus_button_func(key))
        self.plus_buttons[key] = Button(adjustment_container_frame,
                                        text="+",
                                        command=lambda: self.plus_button_func(key))

        # slider value
        self.mod_labels["slider"][key] = ttk.Label(adjustment_container_frame, text=0)

        # race mod
        self.mod_labels["race"][key] = ttk.Label(self, text="0")

        # bio
        self.mod_labels["bio"][key] = ttk.Label(self, text="0")

        # cyber
        self.mod_labels["cyber"][key] = ttk.Label(self, text="0")

        # other mods
        self.mod_labels["other"][key] = ttk.Label(self, text="0")

        # total
        self.mod_labels["total"][key] = ttk.Label(self, text="0")

        # initial output
        self.mod_labels["slider"][key].config(text=str(self.sliders[key].get()))

        # grids
        self.attribute_labels[key].grid(column=0, row=self.current_row, sticky=E)
        adjustment_container_frame.grid(column=1, row=self.current_row)
        # self.sliders[key].grid(column=1, row=self.current_row)
        #self.mod_labels["slider"][key].grid(column=2, row=self.current_row)
        self.mod_labels["race"][key].grid(column=3, row=self.current_row)
        self.mod_labels["bio"][key].grid(column=4, row=self.current_row)
        self.mod_labels["cyber"][key].grid(column=5, row=self.current_row)
        self.mod_labels["other"][key].grid(column=6, row=self.current_row)
        self.mod_labels["total"][key].grid(column=7, row=self.current_row)

        # iterate current row
        self.current_row += 1

    def set_pool_vals(self):
        # set reaction
        self.sliders["reaction"].set(self.statblock.reaction)
        # manually set reaction values
        self.on_set_attribute_value("reaction", self.statblock.reaction, False, False)
        # set dice pool values
        self.combat_pool_val.set(self.statblock.combat_pool)
        self.control_pool_val.set(self.statblock.control_pool)
        self.hacking_pool_val.set(self.statblock.hacking_pool)
        self.spell_pool_val.set(self.statblock.spell_pool)
        self.task_pool_val.set("0")  # NYI
        self.astral_combat_pool_val.set(self.statblock.astral_combat_pool)

    def plus_button_func(self, key):
        karma_cost = (self.statblock.calculate_natural_attribute(key) + 1) * 2
        # check if point purchase is allowed
        if self.statblock.gen_mode.point_purchase_allowed(karma_cost, None):
            self.statblock.base_attributes[key] += 1  # increment it by 1

            # undo function
            def undo():
                self.statblock.base_attributes[key] -= 1
                self.slider_vars[key].set(self.statblock.base_attributes[key])

            new_attr_val = self.statblock.base_attributes[key]

            adjustment = Adjustment(karma_cost, key, undo)
            self.statblock.gen_mode.add_adjustment(adjustment)

            self.slider_vars[key].set(new_attr_val)
            # self.mod_labels["slider"][key].config(text=new_attr_val)
            self.on_set_attribute_value(key, new_attr_val, False, True)
        else:
            print("Can't spend that!")

    def minus_button_func(self, key):
        undo_type = key
        self.statblock.gen_mode.undo(undo_type)
        new_attr_val = self.statblock.base_attributes[key]
        self.slider_vars[key].set(new_attr_val)
        # self.mod_labels["slider"][key].config(text=new_attr_val)
        self.on_set_attribute_value(key, new_attr_val, False, True)

    def adjust_disallowed_purchase(self, key, value):
        """
        Go through the adjustment process attributes changed with the slider. Makes it so that we can't slide
        the slider when a slide would be invalid, like if we don't have enough points to purchase an attribute.
        This won't get called when using buttons, or with reaction.
        :type key: str
        :type value: int
        """

        # test to make sure value is valid
        # add value of all sliders together
        slider_total = self.get_total()

        # We do this because the sliders get the attempted set value rather than the value before the set.
        # We just subtract 1, because we can't go below 0 anyway, and we need to check that we're less than
        # or equal to a threshold in point_purchase_allowed
        # If we don't do this, we'll be limited to a maximum of 1 less than our intended maximum.
        slider_total -= 1

        # if the total is more than the allowed amount of attributes,
        # prevent the purchase
        if not self.statblock.gen_mode.point_purchase_allowed(slider_total, "attributes"):
            value = self.slider_old_vals[key].get()
            self.sliders[key].set(value)
        # if the total is less than or equal to the allowed amount, put the new value in the "old values"
        else:
            self.slider_old_vals[key].set(value)

    def on_set_attribute_value(self, key, value, adjust=True, set_pool=True):
        """Event called when slider is set"""
        # set value to int since it's passed in as a string for some reason
        value = int(value)

        if adjust:
            self.adjust_disallowed_purchase(key, value)

        # we need to int(float(value)) because passes the value in as a string of a floating point number
        self.statblock.base_attributes[key] = value
        # self.mod_labels["slider"][key].config(text=str(self.sliders[key].get()))

        # set slider value column
        slider_val = self.sliders[key].get()
        self.mod_labels["slider"][key].config(text=str(slider_val))

        # set the racial bonus column
        if key == "reaction":  # fuck it hardcode this exception
            race_val = 0
        else:
            race_val = self.race.racial_attributes[key]
        self.mod_labels["race"][key].config(text=race_val)

        # set the bio bonus column
        bio_key = "bio_" + key
        bio_val = StatMod.get_mod_total(bio_key)
        self.mod_labels["bio"][key].config(text=bio_val)

        # set the cyber bonus column
        cyber_key = "cyber_" + key
        cyber_val = StatMod.get_mod_total(cyber_key)
        self.mod_labels["cyber"][key].config(text=cyber_val)

        # set the other bonus column
        other_key = "other_" + key
        other_val = StatMod.get_mod_total(other_key)
        self.mod_labels["other"][key].config(text=other_val)

        # set the total
        total_val = slider_val + race_val + bio_val + cyber_val + other_val
        self.mod_labels["total"][key].config(text=total_val)

        if set_pool:
            # set pool vals
            self.set_pool_vals()

            # recalculate the karma/points/priority/whatever total
            self.calculate_total()

    def setup_derived_attribute(self, key, val):
        self.sliders[key].set(val)
        if key == "essence":
            val = float(val)
        self.mod_labels["total"][key].config(text=val)

    def get_total(self):
        """Returns the total of the value of the sliders of the base attributes."""

        total = 0
        for attribute in self.base_attributes:
            val = self.sliders[attribute]
            total += val.get()  # + 1

        return total

    def calculate_total(self):
        """Totals all attributes' point values and updates the top karma bar."""
        total = 0

        self.statblock.gen_mode.update_total(self.get_total(), "attributes")

    def racial_slider_calc(self, key):
        """Gets the total of the slider value and the racial attribute mod."""
        slider_val = self.sliders[key].get()
        return slider_val + self.race.racial_attributes[key]

    def load_character(self):
        """Called whenever a character is loaded"""
        for key in AttributesTab.base_attributes:
            # basically simulate setting each value with the slider
            value = self.statblock.base_attributes[key]
            self.sliders[key].set(value)
            self.on_set_attribute_value(key, value)
        self.on_switch()

    def get_progress_bar_info(self):
        cur = self.character.statblock.gen_mode.cur_attribute_points.get()
        max = self.character.statblock.gen_mode.max_attribute_points.get()

        return cur, max

    def on_switch(self):
        # pack forget buttons and sliders to reset ui
        for item in list(self.sliders.values())\
                    + list(self.minus_buttons.values())\
                    + list(self.plus_buttons.values())\
                    + list(self.mod_labels["slider"].values()):
            item.pack_forget()

        self.race_label.config(text=self.race.name)
        for key in AttributesTab.base_attributes:

            if type(self.statblock.gen_mode) != Finalized:
                # pack the slider
                self.sliders[key].pack(side=LEFT)
                self.mod_labels["slider"][key].pack()

            else:
                # remove the hard limits on attributes
                # we shouldn't ever need to undo this because you can't un-finalize a character
                self.sliders[key].configure(to=99)
                # setup plus and minus buttons
                self.minus_buttons[key].pack(side=LEFT, padx=5)
                self.mod_labels["slider"][key].pack(side=LEFT, padx=5)
                self.plus_buttons[key].pack(side=LEFT, padx=5)

                # change the command callback?

            # setup the sliders
            # we do this regardless of finalization or not because the sliders still exist in the finalized state,
            # they're just hidden

            # set slider minimum
            racial_slider_minimum = self.race.racial_slider_minimum(key)
            self.sliders[key].config(from_=racial_slider_minimum)

            # set slider to the lowest of the current value and the racial minimum
            # this way races like trolls and orks will buy up new shit
            slider_set_val = max(self.sliders[key].get(), racial_slider_minimum)
            self.sliders[key].set(slider_set_val)
            self.on_set_attribute_value(key, slider_set_val)

        self.setup_derived_attribute("essence", self.statblock.essence)
        self.setup_derived_attribute("magic", self.statblock.magic)
        self.setup_derived_attribute("reaction", self.statblock.reaction)
