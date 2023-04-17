from abc import ABC

from src.CharData.gear import Gear
from src.GenModes.finalized import Finalized
from src.Tabs.notebook_tab import NotebookTab
from tkinter import *
from tkinter import ttk
from typing import Dict, List

from src.adjustment import Adjustment
from src.statblock_modifier import StatMod


class AttributesTab(NotebookTab, ABC):
    equipped_armors: List[Gear]
    sliders: Dict[str, Scale]
    slider_vars: Dict[str, IntVar]
    attribute_labels: Dict[str, ttk.Label]
    mod_labels: Dict[str, Dict[str, ttk.Label]]

    base_attributes = ["body", "quickness", "strength", "charisma", "intelligence", "willpower"]
    derived_attributes = ["essence", "magic", "reaction", "initiative"]

    def __init__(self, parent):
        super().__init__(parent, "AttributesTab")

        self.equipped_armors = []

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
            self.setup_slider_and_label(attr, first_setup=TRUE)

        for attr in AttributesTab.derived_attributes:
            self.setup_slider_and_label(attr, True, first_setup=TRUE)

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

        # armor variables
        self.ballistic_armor_val = StringVar()
        self.ballistic_armor_val.set("0")
        self.impact_armor_val = StringVar()
        self.impact_armor_val.set("0")
        self.quickness_penalty_val = StringVar()
        self.quickness_penalty_val.set("0")

        # set dice pool values
        self.boot_pool_vals()

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
            textvariable=self.combat_pool_val
        )
        self.combat_pool_val_label.grid(column=1, row=0)

        self.control_pool_val_label = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvariable=self.control_pool_val
        )
        self.control_pool_val_label.grid(column=1, row=1)

        self.hacking_pool_val_label = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvariable=self.hacking_pool_val
        )
        self.hacking_pool_val_label.grid(column=1, row=2)

        self.spell_pool_val_label = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvariable=self.spell_pool_val
        )
        self.spell_pool_val_label.grid(column=1, row=3)

        self.task_pool_val_label = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvariable=self.task_pool_val
        )
        self.task_pool_val_label.grid(column=1, row=4)

        self.astral_combat_pool_label_labelframe = ttk.Label(
            self.dice_pool_labelframe,
            style="Red.TLabel",
            textvariable=self.astral_combat_pool_val
        )
        self.astral_combat_pool_label_labelframe.grid(column=1, row=5)

        # setup the other attributes
        self.sliders["essence"].set(6)

        # setup armor labelframe
        self.armor_labelframe = ttk.LabelFrame(self, text="Armor")
        self.armor_labelframe.grid(column=8, row=6, rowspan=2)

        # armor label
        self.ballistic_armor_label = ttk.Label(self.armor_labelframe, text="Ballistic: ")
        self.ballistic_armor_label.grid(column=0, row=0)

        self.impact_armor_label = ttk.Label(self.armor_labelframe, text="Impact: ")
        self.impact_armor_label.grid(column=0, row=1)

        self.quickness_penalty_label = ttk.Label(self.armor_labelframe, text="Quickness Penalty: ")
        self.quickness_penalty_label.grid(column=0, row=2)

        # armor values
        self.ballistic_armor_val_label = ttk.Label(
            self.armor_labelframe,
            style="Red.TLabel",
            textvariable=self.ballistic_armor_val
        )
        self.ballistic_armor_val_label.grid(column=1, row=0)

        self.impact_armor_val_label = ttk.Label(
            self.armor_labelframe,
            style="Red.TLabel",
            textvariable=self.impact_armor_val
        )
        self.impact_armor_val_label.grid(column=1, row=1)

        self.quickness_penalty_val_label = ttk.Label(
            self.armor_labelframe,
            style="Red.TLabel",
            textvariable=self.quickness_penalty_val
        )
        self.quickness_penalty_val_label.grid(column=1, row=2)

    def setup_slider_and_label(self, key, other_attribute=False, first_setup=False):
        """Initial setup. Should only be run once per attribute."""
        self.slider_vars[key] = IntVar()  # this is the internal variable
        self.slider_vars[key].set(1)  # initialize it to 1
        self.slider_old_vals[key] = IntVar()  # this is to correct for when we try to go over our total
        self.slider_old_vals[key].set(1)  # initialize it to 1

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
        elif first_setup:  # just set to 1 if it's the very first setup on boot
            racial_slider_minimum = 1
        else:
            racial_slider_minimum = self.race.racial_slider_minimum(key)

        # The from_ and to values on the sliders themselves are different from
        # what the actual values are.
        self.sliders[key] = Scale(adjustment_container_frame,
                                  from_=racial_slider_minimum, to=6,
                                  variable=self.slider_vars[key],
                                  command=lambda x: self.on_set_attribute_value(key, x),
                                  orient=HORIZONTAL, showvalue=False)

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
        # self.mod_labels["slider"][key].grid(column=2, row=self.current_row)
        self.mod_labels["race"][key].grid(column=3, row=self.current_row)
        self.mod_labels["bio"][key].grid(column=4, row=self.current_row)
        self.mod_labels["cyber"][key].grid(column=5, row=self.current_row)
        self.mod_labels["other"][key].grid(column=6, row=self.current_row)
        self.mod_labels["total"][key].grid(column=7, row=self.current_row)

        # iterate current row
        self.current_row += 1

    def boot_pool_vals(self):
        # boots all the pools with value 1 for initial program load

        # set reaction
        self.sliders["reaction"].set(1)
        self.sliders["initiative"].set(1)

        # set dice pool values
        self.combat_pool_val.set("1")
        self.control_pool_val.set("1")
        self.hacking_pool_val.set("1")
        self.spell_pool_val.set("1")
        self.task_pool_val.set("0")  # NYI
        self.astral_combat_pool_val.set("1")

    def set_pool_vals(self):
        # setting reaction slider gives proper value, setting initiative slider does not
        # yet both call on_set_attribute_value, test this

        # set reaction
        self.sliders["reaction"].set(self.statblock.base_reaction)
        # set initiative, maybe find a better place to do this?
        # self.sliders["initiative"].set(self.statblock.initiative)
        # manually set reaction values
        self.on_set_attribute_value("reaction", self.statblock.reaction, False, False)
        self.on_set_attribute_value("initiative", self.statblock.initiative, False, False)
        # set dice pool values
        self.combat_pool_val.set(self.statblock.combat_pool)
        self.control_pool_val.set(self.statblock.control_pool)
        self.hacking_pool_val.set(self.statblock.hacking_pool)
        self.spell_pool_val.set(self.statblock.spell_pool)
        self.task_pool_val.set("0")  # NYI
        self.astral_combat_pool_val.set(self.statblock.astral_combat_pool)

    def plus_button_func(self, key):
        # check if we're at the absolute maximum
        if self.statblock.base_attributes[key] >= self.statblock.race.racial_max(key):
            print(f"{key} already at maximum!")
            return

        if self.statblock.base_attributes[key] >= self.statblock.race.racial_limit(key):
            karma_cost = (self.statblock.calculate_natural_attribute(key) + 1) * 3
        else:
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
        if key in self.statblock.base_attributes:
            self.statblock.base_attributes[key] = value
        # self.mod_labels["slider"][key].config(text=str(self.sliders[key].get()))

        # set slider value column
        slider_val = self.sliders[key].get()
        self.mod_labels["slider"][key].config(text=str(slider_val))

        # set the racial bonus column
        if key == "reaction" or key == "initiative":  # fuck it hardcode this exception
            race_val = 0
        else:
            race_val = int(self.race.racial_attributes[key])
        self.mod_labels["race"][key].config(text=race_val)

        # set the bio bonus column
        bio_key = "bio_" + key
        bio_val = int(StatMod.get_mod_total(bio_key))
        self.mod_labels["bio"][key].config(text=bio_val)

        # set the cyber bonus column
        cyber_key = "cyber_" + key
        cyber_val = int(StatMod.get_mod_total(cyber_key))
        self.mod_labels["cyber"][key].config(text=cyber_val)

        # set the other bonus column
        other_key = "other_" + key
        other_val = int(StatMod.get_mod_total(other_key))
        self.mod_labels["other"][key].config(text=other_val)

        # set the total, force it to be an integer
        total_val = int(slider_val + race_val + bio_val + cyber_val + other_val)
        self.mod_labels["total"][key].config(text=total_val)

        if set_pool:
            # set pool vals
            self.set_pool_vals()

            # recalculate the karma/points/priority/whatever total
            self.calculate_total()

        # recalculate armor penalties and shit when we change quickness
        if key == "quickness":
            self.statblock.calculate_armor_and_penalties(self.equipped_armors, None, None)
            self.quickness_penalty_val.set(self.statblock.armor_quickness_penalty)

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
        _cur = self.character.statblock.gen_mode.cur_attribute_points.get()
        _max = self.character.statblock.gen_mode.max_attribute_points.get()

        return _cur, _max

    def on_switch(self):
        # pack forget buttons and sliders to reset ui
        forgets = list(self.sliders.values()) \
                + list(self.minus_buttons.values()) \
                + list(self.plus_buttons.values()) \
                + list(self.mod_labels["slider"].values())
        for item in forgets:
            item.pack_forget()

        # get name of current race and set the label
        self.race_label.config(text=self.race.name)

        # get a list of equipped armors
        self.equipped_armors = list(filter(lambda x: "equipped" in x.properties and x.properties["equipped"] is True,
                                           self.statblock.inventory))

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
        self.setup_derived_attribute("reaction", self.statblock.base_reaction)

        # this is done so that we update reaction properly when we switch to this tab
        self.on_set_attribute_value("reaction", self.statblock.base_reaction)

        # setup armor
        bal_total = self.statblock.ballistic_armor + StatMod.get_mod_total("race_ballistic") \
                                                   + StatMod.get_mod_total("bio_ballistic") \
                                                   + StatMod.get_mod_total("cyber_ballistic") \
                                                   + StatMod.get_mod_total("other_ballistic")
        self.ballistic_armor_val.set(bal_total)

        imp_total = self.statblock.impact_armor + StatMod.get_mod_total("race_impact") \
                                                + StatMod.get_mod_total("bio_impact") \
                                                + StatMod.get_mod_total("cyber_impact") \
                                                + StatMod.get_mod_total("other_impact")
        self.impact_armor_val.set(imp_total)

        self.quickness_penalty_val.set(self.statblock.armor_quickness_penalty)
