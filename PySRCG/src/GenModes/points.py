from tkinter import *
from tkinter import ttk

from abc import ABC

from src import app_data
from src.GenModes.gen_mode import GenMode
from src.utils import magic_tab_show_on_awakened_status


class Points(GenMode, ABC):
    # key = nuyen, val = point cost
    resource_amounts = (500, 5000, 20000, 90000, 200000, 400000, 1000000)
    resource_costs = (-5, 0, 5, 10, 20, 25, 30)
    otaku_resource_amounts = ("Squatter (0 points)", "Low (5 points)", "Middle (10 points)",
                              "High (15 points)", "Luxury (20 points)")
    otaku_resource_costs = (0, 5, 10, 15, 20)

    old_money_value = 0

    # setup metatype combobox
    metatype_options = []
    awakened_var = None

    # setup listbox list for resources
    resource_options = []

    cur_skill_points = None
    cur_magic_points = None
    cur_attribute_points = None
    cur_edge_flaw_points = None

    max_skill_points = None
    max_magic_points = None
    max_attribute_points = None

    # blank things so we hold them here
    metatype_combobox = None
    resource_combobox = None
    attribute_label = None
    attribute_spinbox = None
    skill_label = None
    skill_spinbox = None
    full_radio = None
    aspected_radio = None
    mundane_radio = None

    @staticmethod
    def setup_ui_elements():
        super(Points, Points).setup_ui_elements()

        Points.cur_skill_points = IntVar()
        Points.cur_magic_points = IntVar()
        Points.cur_attribute_points = IntVar()
        Points.cur_edge_flaw_points = IntVar()

        Points.max_skill_points = IntVar()
        Points.max_magic_points = IntVar()
        Points.max_attribute_points = IntVar()

        Points.awakened_var = StringVar()
        Points.otaku_var = BooleanVar()
        Points.runt_otaku_var = BooleanVar()

        Points.resource_combobox = ttk.Combobox(GenMode.parent.gen_mode_frame,
                                                values=Points.resource_options, state="readonly")

        Points.attribute_label = ttk.LabelFrame(GenMode.parent.gen_mode_frame, text="Attribute Points")
        Points.attribute_spinbox = ttk.Spinbox(Points.attribute_label, from_=6,
                                               textvariable=Points.max_attribute_points)
        Points.attribute_spinbox.pack()

        Points.skill_label = ttk.LabelFrame(GenMode.parent.gen_mode_frame, text="Skill Points")
        Points.skill_spinbox = ttk.Spinbox(Points.skill_label, from_=0, textvariable=Points.max_skill_points)
        Points.skill_spinbox.pack()

        Points.full_radio = Radiobutton(GenMode.parent.gen_mode_frame, variable=Points.awakened_var,
                                        text="Full Magician (30 pts)", value="Full")
        Points.aspected_radio = Radiobutton(GenMode.parent.gen_mode_frame, variable=Points.awakened_var,
                                            text="Aspected (25 pts)", value="Aspected")
        Points.mundane_radio = Radiobutton(GenMode.parent.gen_mode_frame, variable=Points.awakened_var,
                                           text="Mundane (0 pts)", value="Mundane")

        Points.awakened_var.set("Mundane")

    def __init__(self, data=None, **kwargs):
        super().__init__()
        self.purchased_magic_points = IntVar()
        self.max_points = IntVar(value=120)  # eventually change this to some option
        self.starting_skills_max = 6

        if type(data) is dict and "attribute_points" in data:
            self.attribute_points = data["attribute_points"]
        else:
            if Points.max_attribute_points.get() == 0:
                self.attribute_points = 12
            else:
                self.attribute_points = Points.max_attribute_points.get()

        if type(data) is dict and "skill_points" in data:
            self.skill_points = data["skill_points"]
        else:
            if Points.max_skill_points.get() == 0:
                self.skill_points = 24
            else:
                self.skill_points = Points.max_skill_points.get()

        if type(data) is dict and "awakened" in data:
            Points.awakened_var.set(data["awakened"])

        if app_data.app_character.statblock.otaku:
            self.awakened_var.set("Mundane")
            self.full_radio.config(state=DISABLED)
            self.aspected_radio.config(state=DISABLED)
            self.mundane_radio.config(state=DISABLED)


        """
        sr3 allows purchasing extra spell points at 25000 each
        Note that these are also added to max_magic_points when purchased, this is only for tracking 
        how many of those points are purchased separately.
        """
        self.purchased_magic_points = IntVar()
        if "purchased_magic_points" in kwargs:
            self.purchased_magic_points.set(kwargs["purchased_magic_points"])
            p = self.max_magic_points.get()
            self.max_magic_points.set(p + self.purchased_magic_points.get())
        else:
            self.purchased_magic_points.set(0)

        Points.max_attribute_points.set(self.attribute_points)
        Points.max_skill_points.set(self.skill_points)

        Points.cur_attribute_points.set(12)
        Points.cur_skill_points.set(self.max_points.get() - Points.max_attribute_points.get())

        # trace vars
        Points.max_attribute_points.trace("w", lambda x, y, z: self.set_spinbox_limits())
        Points.max_skill_points.trace("w", lambda x, y, z: self.set_spinbox_limits())

        Points.full_radio.config(command=self.on_awakened_change)
        Points.aspected_radio.config(command=self.on_awakened_change)
        Points.mundane_radio.config(command=self.on_awakened_change)

        Points.resource_combobox.bind("<<ComboboxSelected>>",
                                      lambda ignore_event: self.on_change_resources(Points.old_money_value))

        self.magic_costs = {
            "Full": 30,
            "Aspected": 25,
            "Mundane": 0
        }

        self.karma_bar_vals = {
            "attributes": (self.cur_attribute_points, self.max_attribute_points),
            "spells": (self.cur_magic_points, self.max_magic_points),
            "skills": (self.cur_skill_points, self.max_skill_points),
        }

        self.used_points = IntVar()
        self.fill_valid_resources()
        self.set_spinbox_limits()

        # force -5 only resources for testing
        if data is not None and "resources" in data:
            Points.resource_combobox.current(data["resources"])
            Points.old_money_value = Points.resource_amounts[data["resources"]]

        if Points.resource_combobox.current() == -1:
            Points.resource_combobox.current(1)
            Points.old_money_value = Points.resource_amounts[1]

    def update_total(self, amount, key):
        if key == "attributes":
            self.cur_attribute_points.set(amount)
            app_data.top_bar.update_karma_label(self.cur_attribute_points.get(),
                                                self.max_attribute_points.get(),
                                                "Points Mode")

        elif key == "skills":
            self.cur_skill_points.set(amount)
            app_data.top_bar.update_karma_label(self.cur_skill_points.get(),
                                                self.max_skill_points.get(),
                                                "Points Mode")
        elif key == "magic":
            self.cur_magic_points.set(amount)
            app_data.top_bar.update_karma_label(self.cur_magic_points.get(),
                                                self.max_magic_points.get(),
                                                "Points Mode")

        elif key == "points":
            self.calc_remaining_points()
            self.fill_valid_resources()
            self.fill_valid_metatypes()
            app_data.top_bar.update_karma_label(self.used_points.get(),
                                                self.max_points.get(),
                                                "Points Mode")

    def magic_val_from_string(self):
        awakened_type = self.get_generated_value("magic")
        if awakened_type == "Full":
            return 25
        elif awakened_type == "Aspected":
            return 35
        else:
            return 0

    def point_purchase_allowed(self, amount, key):
        if key == "skills":
            threshold = self.max_skill_points.get()
        elif key == "magic":
            threshold = self.max_magic_points.get()
        elif key == "attributes":
            threshold = self.max_attribute_points.get()
        else:
            raise ValueError('key must be "skills", "magic", or "attributes"')

        if amount >= threshold:
            return False
        else:
            return True

    def increment_purchased_magic_points(self):
        p = self.purchased_magic_points.get()
        self.purchased_magic_points.set(p + 1)
        p = self.max_magic_points.get()
        self.max_magic_points.set(p + 1)

    def decrement_purchased_magic_points(self):
        """
        Returns True and decrements purchased magic points if possible to do so.
        Otherwise, returns False.
        """
        if self.purchased_magic_points.get() > 0:
            p = self.purchased_magic_points.get()
            self.purchased_magic_points.set(p - 1)
            p = self.max_magic_points.get()
            self.max_magic_points.set(p - 1)
            return True
        else:
            return False

    def on_change_resources(self, old_money):
        if not app_data.app_character.statblock.otaku:
            new_money = Points.resource_amounts[Points.resource_combobox.current()]
            money_diff = new_money - old_money
            app_data.app_character.statblock.add_cash(money_diff)
            Points.old_money_value = new_money
        else:  # must be set every time to prevent bugs
            Points.old_money_value = 5000
        self.update_total(None, "points")

    def on_awakened_change(self):
        # set magic
        awakened_val = self.get_generated_value("magic")

        # always override to "Mundane" if otaku
        if app_data.app_character.statblock.otaku:
            awakened_val = "Mundane"

        # set aspect to Full Mage if magic is top priority
        if awakened_val == "Full":
            app_data.app_character.statblock.aspect = "Full Mage"
        # refund all purchased spell points if set to mundane
        elif awakened_val == "Mundane":
            refund_value = 25000 * self.purchased_magic_points.get()
            self.purchased_magic_points.set(0)
            app_data.app_character.statblock.add_cash(refund_value)

        app_data.app_character.statblock.awakened = awakened_val

        self.max_magic_points.set(self.magic_val_from_string() + self.purchased_magic_points.get())

        magic_tab_show_on_awakened_status(app_data)
        self.update_total(None, "points")

    def set_spinbox_limits(self):
        try:
            self.attribute_points = Points.max_attribute_points.get()
        except TclError:
            self.attribute_points = 0
        try:
            self.skill_points = Points.max_skill_points.get()
        except TclError:
            self.skill_points = 0
        self.update_total(None, "points")
        remaining = self.get_remaining_points()
        Points.attribute_spinbox.config(to=self.attribute_points + remaining // 2)
        Points.skill_spinbox.config(to=self.skill_points + remaining)

    def on_metatype_selected(self):
        self.update_total(None, "points")

    def on_set_otaku(self) -> bool:
        if not app_data.app_character.statblock.otaku:
            raise ValueError("Should be otaku to call on_set_otaku()!")

        # check if we have enough points
        # just get the old calculated point value as it should be fine
        remaining_points = self.max_points.get() - self.used_points.get()
        # if we have -5 from resources, sub 5 from remaining points, we'll lose those after if we set to otaku
        old_money = self.get_generated_value("resources")
        if old_money == 500:
            remaining_points -= 5

        if remaining_points < 30:
            print("Not enough points to become an otaku!")
            return False

        new_money = 5000

        money_diff = new_money - old_money
        # money check
        if app_data.app_character.statblock.cash + money_diff < 0:
            print("Not enough money to become an otaku!")
            return False
        app_data.app_character.statblock.add_cash(money_diff)

        # lock awakened
        self.awakened_var.set("Mundane")
        self.full_radio.config(state=DISABLED)
        self.aspected_radio.config(state=DISABLED)
        self.mundane_radio.config(state=DISABLED)

        # correct resources, set to squatter
        self.resource_combobox.current(0)
        self.fill_valid_resources()
        self.resource_combobox.current(0)
        self.calc_remaining_points()  # recalc after set
        self.update_total(None, "points")

        return True

    def on_unset_otaku(self):
        if app_data.app_character.statblock.otaku:
            raise ValueError("Should not be otaku to call on_set_otaku()!")

        # correct resources, set to 5000
        self.calc_remaining_points()
        self.resource_combobox.current(0)
        self.fill_valid_resources()
        self.resource_combobox.current(1)
        self.calc_remaining_points()  # recalc after set
        self.update_total(None, "points")

        # unlock awakened
        self.full_radio.config(state=NORMAL)
        self.aspected_radio.config(state=NORMAL)
        self.mundane_radio.config(state=NORMAL)

        return True

    def get_otaku_complex_forms_resources(self):
        return 0  # NYI

    def grid_ui_elements(self):
        super().grid_ui_elements()

        # grids
        Points.resource_combobox.grid(column=0, row=1)
        Points.attribute_label.grid(column=0, row=2)
        Points.skill_label.grid(column=0, row=3)
        Points.full_radio.grid(column=0, row=4)

        Points.aspected_radio.grid(column=0, row=5)

        Points.mundane_radio.grid(column=0, row=6)

    def get_remaining_points(self):
        return self.max_points.get() - self.used_points.get()

    def calc_remaining_points(self):
        total = self.max_points.get()
        total -= self.attribute_points * 2  # attribute points are worth double
        total -= self.skill_points
        total -= app_data.app_character.statblock.metatype.point_cost
        c = Points.resource_combobox.current()
        
        # avoid unselected bug
        if c != -1:
            if app_data.app_character.statblock.otaku:
                total -= Points.otaku_resource_costs[Points.resource_combobox.current()]
                total -= 30  # sub otaku cost
            else:
                total -= Points.resource_costs[Points.resource_combobox.current()]
        total -= self.magic_costs[self.awakened_var.get()]

        # disable unselected awakened radiobuttons we can't afford
        total_without_magic = total + self.magic_costs[self.awakened_var.get()]
        if not app_data.app_character.statblock.otaku:
            if total_without_magic < self.magic_costs["Full"]:
                self.full_radio.config(state=DISABLED)
            else:
                self.full_radio.config(state=NORMAL)
            if total_without_magic < self.magic_costs["Aspected"]:
                self.aspected_radio.config(state=DISABLED)
            else:
                self.aspected_radio.config(state=NORMAL)

        # set used points
        self.used_points.set(self.max_points.get() - total)
        return total

    def get_generated_value(self, key):
        generation_dict = {
            "resources": Points.resource_amounts[Points.resource_combobox.current()],
            "skills": self.skill_points,
            "attributes": self.attribute_points,
            "metatype": app_data.app_character.statblock.metatype.point_cost,
            "magic": self.awakened_var.get()
        }

        # if app_data.app_character.statblock.otaku:
        #     generation_dict["resources"] = 5000

        return generation_dict[key]

    def fill_valid_metatypes(self):
        super().fill_valid_metatypes()
        remaining = self.get_remaining_points()

        # do not count the metatype we've already selected in the calculation
        remaining += app_data.app_character.statblock.metatype.point_cost

        for metatype_name in app_data.game_data["Metatypes"]:
            metatype_cost = app_data.game_data["Metatypes"][metatype_name]["point_cost"]
            if metatype_cost <= remaining:
                GenMode.parent.metatype_listbox_values.append(f"{metatype_name}: {metatype_cost} points")
                GenMode.parent.metatype_keys.append(metatype_name)

        GenMode.parent.metatype_box.config(values=GenMode.parent.metatype_listbox_values)

    def fill_valid_resources(self):
        Points.resource_options.clear()
        remaining = self.get_remaining_points()

        # do not count the resources we've already selected in the calculation
        if app_data.app_character.statblock.otaku:
            remaining += Points.otaku_resource_costs[Points.resource_combobox.current()]

            for i in range(0, len(Points.otaku_resource_amounts)):
                key = Points.otaku_resource_amounts[i]
                val = Points.otaku_resource_costs[i]
                if val <= remaining:
                    Points.resource_options.append(key)
        else:
            remaining += Points.resource_costs[Points.resource_combobox.current()]

            for i in range(0, len(Points.resource_amounts)):
                key = Points.resource_amounts[i]
                val = Points.resource_costs[i]
                if val <= remaining:
                    Points.resource_options.append(f"¥{key}: {val} points")

        Points.resource_combobox.config(values=Points.resource_options)

    def serialize(self):
        return {"type": "points",
                "data": {
                    "attribute_points": self.attribute_points,
                    "skill_points": self.skill_points,
                    "awakened": self.awakened_var.get(),
                    "resources": self.resource_combobox.current()
                },
                "purchased_magic_points": self.purchased_magic_points.get()}
