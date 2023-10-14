from abc import ABC

from tkinter import *

from src import app_data
from src.CharData.metatype import Metatype
from src.GenModes.gen_mode import GenMode
from src.utils import magic_tab_show_on_awakened_status


def points_max():
    return app_data.app_character.statblock.magic + app_data.app_character.statblock.bonus_power_points


class Priority(GenMode, ABC):
    priority_name_list = None
    priority_vals_list = None
    up_button = None
    down_button = None

    cur_skill_points = None
    cur_magic_points = None
    cur_attribute_points = None
    cur_edge_flaw_points = None

    max_skill_points = None
    max_magic_points = None
    max_attribute_points = None
    
    def __init__(self, data=None, **kwargs):
        super().__init__()
        self.starting_skills_max = 6

        # 0 is the highest priority, 4 is lowest
        if data is None:
            self.priority_order = ["resources", "attributes", "metatype", "skills", "magic"]
        else:
            self.priority_order = data

        # this _dict corresponds to the value of the priority of each option
        # e.g. magic C would be priority_value_dict["magic"][2]
        self.priority_value_dict = {
            "resources": [1000000, 400000, 90000, 20000, 5000],
            "attributes": [30, 27, 24, 21, 18],
            "metatype": [["Elf", "Troll", "Dwarf", "Ork", "Human"],
                         ["Elf", "Troll", "Dwarf", "Ork", "Human"],
                         ["Elf", "Troll", "Dwarf", "Ork", "Human"],
                         ["Dwarf", "Ork", "Human"],
                         ["Human"]],
            "skills": [50, 40, 34, 30, 27],
            "magic": ["Full", "Aspected", "Mundane", "Mundane", "Mundane"]
        }

        Priority.max_skill_points.set(self.get_generated_value("skills"))
        Priority.max_magic_points.set(self.magic_val_from_string())
        Priority.max_attribute_points.set(self.get_generated_value("attributes"))

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

        # this dict is for getting karma bar stuff
        # first in tuple is current, second in tuple is max
        self.karma_bar_vals = {
            "attributes": (self.cur_attribute_points, self.max_attribute_points),
            "spells": (self.cur_magic_points, self.max_magic_points),
            "skills": (self.cur_skill_points, self.max_skill_points),
        }

        # set up and down commands
        Priority.up_button.config(command=lambda: self.swap_priority(-1))
        Priority.down_button.config(command=lambda: self.swap_priority(1))

    @staticmethod
    def setup_ui_elements():
        Priority.cur_skill_points = IntVar()
        Priority.cur_magic_points = IntVar()
        Priority.cur_attribute_points = IntVar()
        Priority.cur_edge_flaw_points = IntVar()

        Priority.max_skill_points = IntVar()
        Priority.max_magic_points = IntVar()
        Priority.max_attribute_points = IntVar()

        Priority.up_button = Button(GenMode.parent.gen_mode_frame, text="↑")
        Priority.down_button = Button(GenMode.parent.gen_mode_frame, text="↓")

        Priority.priority_name_list = Listbox(GenMode.parent.gen_mode_frame, height=5,
                                              selectmode=SINGLE, exportselection=0)
        Priority.priority_name_list.bind("<<ListboxSelect>>", Priority.sync_list_selected)
        Priority.priority_vals_list = Listbox(GenMode.parent.gen_mode_frame, height=5,
                                              selectmode=SINGLE, exportselection=0)
        Priority.priority_vals_list.bind("<<ListboxSelect>>", Priority.sync_list_selected)

    def grid_ui_elements(self):
        super().grid_ui_elements()

        Priority.up_button.grid(column=2, row=1)
        Priority.down_button.grid(column=2, row=2)
        Priority.priority_name_list.grid(column=0, row=1, columnspan=2, rowspan=2)
        Priority.priority_vals_list.grid(column=3, row=1, columnspan=2, rowspan=2)

        self.fill_lists()

    def fill_valid_metatypes(self):
        super().fill_valid_metatypes()
        metatype_rank = self.priority_order.index("metatype")
        for meta_k, meta_v in app_data.game_data["Metatypes"].items():
            if meta_v["priority_rank"] >= metatype_rank:
                GenMode.parent.metatype_listbox_values.append(meta_k)
                GenMode.parent.metatype_keys.append(meta_k)

        GenMode.parent.metatype_box.config(values=GenMode.parent.metatype_listbox_values)

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

    def point_purchase_allowed(self, amount: int, key: str) -> bool:
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

    def update_total(self, amount, key):
        if key == "attributes":
            self.cur_attribute_points.set(amount)
            app_data.top_bar.update_karma_label(self.cur_attribute_points.get(),
                                                self.max_attribute_points.get(),
                                                "Priority Mode")

        elif key == "skills":
            self.cur_skill_points.set(amount)
            app_data.top_bar.update_karma_label(self.cur_skill_points.get(),
                                                self.max_skill_points.get(),
                                                "Priority Mode")
        elif key == "magic":
            self.cur_magic_points.set(amount)
            app_data.top_bar.update_karma_label(self.cur_magic_points.get(),
                                                self.max_magic_points.get(),
                                                "Priority Mode")

    def swap_priority(self, direction):
        """
        Direction should be -1 for up or 1 for down
        @param direction: int
        @return: None
        """
        # do nothing if nothing is selected
        if len(self.priority_name_list.curselection()) == 0:
            return

        if app_data.app_character is not None:
            # do nothing if we're an otaku with magic selected
            magic_selected = self.priority_order[self.priority_name_list.curselection()[0]] == "magic"
            swapping_to_magic = self.priority_name_list.curselection()[0] == 1 and direction == -1
            if app_data.app_character.statblock.otaku:
                if magic_selected or swapping_to_magic:
                    return

        # do nothing if we're otaku and swapping with magic

        selected_item_index = self.priority_name_list.curselection()[-1]
        swap_index = selected_item_index + direction

        # do nothing if we'd go out of bounds
        if swap_index > 4 or swap_index < 0:
            return

        # get old money val before swap
        old_money = self.get_generated_value("resources")

        # do the swap
        # self.swap_priority_list_positions(selected_item_index, swap_index)
        self.priority_order[selected_item_index], self.priority_order[swap_index] = \
            self.priority_order[swap_index], self.priority_order[selected_item_index]

        # rewrite the lists
        self.fill_lists()
        self.priority_name_list.selection_clear(0, END)
        self.priority_vals_list.selection_clear(0, END)
        self.priority_name_list.selection_set(swap_index)
        self.priority_vals_list.selection_set(swap_index)

        self.fill_valid_metatypes()
        self.on_priority_change(old_money)

    # gets the magic point value from a string like Full or Aspected
    def magic_val_from_string(self):
        awakened_type = self.get_generated_value("magic")
        if awakened_type == "Full":
            return 25
        elif awakened_type == "Aspected":
            return 35
        else:
            return 0

    def on_priority_change(self, old_money):
        """set old values to new ones"""
        self.max_attribute_points.set(self.get_generated_value("attributes"))
        self.max_magic_points.set(self.magic_val_from_string() + self.purchased_magic_points.get())
        self.max_skill_points.set(self.get_generated_value("skills"))

        # breaking scope like this is SO hacky but fuck it
        # set money, skip this step if we're otaku
        if not app_data.app_character.statblock.otaku:
            money_diff = self.get_generated_value("resources") - old_money
            app_data.app_character.statblock.add_cash(money_diff)

        # reset to human if metatype isn't valid
        if app_data.app_character.statblock.metatype.name not in self.get_generated_value("metatype"):
            app_data.app_character.statblock.metatype = \
                Metatype(name="Human", **app_data.game_data["Metatypes"]["Human"])
            GenMode.parent.metatype_box.set("Human")

        # set magic
        awakened_val = self.get_generated_value("magic")

        # always override to None if otaku
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

        magic_tab_show_on_awakened_status(app_data)

    @staticmethod
    def sync_list_selected(event):
        # figure out which we clicked
        if event.widget is Priority.priority_name_list:
            clicked_widget = Priority.priority_name_list
            syncing_widget = Priority.priority_vals_list
        else:
            clicked_widget = Priority.priority_vals_list
            syncing_widget = Priority.priority_name_list

        # sync the one we didn't click to that one
        syncing_widget.selection_clear(0, END)
        active_index = clicked_widget.index(ANCHOR)
        syncing_widget.selection_set(active_index)

    def fill_lists(self):
        # clear both lists
        self.priority_name_list.delete(0, END)
        self.priority_vals_list.delete(0, END)

        # fill both lists
        L = self.pretty_priority_values()
        for i in range(0, 5):
            # rename magic to otaku if otaku
            if app_data.app_character is not None \
                    and app_data.app_character.statblock.otaku \
                    and self.priority_order[i] == "magic":
                self.priority_name_list.insert(END, "otaku")
            else:
                self.priority_name_list.insert(END, self.priority_order[i])
            self.priority_vals_list.insert(END, L[i])

    def on_metatype_selected(self):
        # do nothing
        pass

    def pretty_priority_values(self):
        L = self.priority_values()

        # find cash
        cash_index = self.priority_order.index("resources")
        L[cash_index] = "¥" + str(L[cash_index])
        # find metatype
        metatype_index = self.priority_order.index("metatype")
        if metatype_index == 4:
            L[metatype_index] = "Human"
        elif metatype_index == 3:
            L[metatype_index] = "Dwarf/Ork"
        elif metatype_index == 2:
            L[metatype_index] = "Elf/Troll"
        else:
            L[metatype_index] = "Any Metatype"
        # find magic
        magic_index = self.priority_order.index("magic")
        if magic_index == 0:
            if app_data.app_character.statblock.otaku:
                L[magic_index] = "Otaku"
            else:
                L[magic_index] = "Full Mage"
        elif magic_index == 1:
            L[magic_index] = "Aspected Mage"
        else:
            L[magic_index] = "Mundane"

        return L

    def get_generated_value(self, key):
        return self.priority_value_dict[key][self.priority_order.index(key)]

    def priority_values(self):
        """This one is the raw data for the current values"""
        L = []

        for i in range(0, 5):
            val = self.priority_order[i]
            L.append(self.priority_value_dict[val][i])

        return L

    def on_set_otaku(self) -> bool:
        if not app_data.app_character.statblock.otaku:
            raise ValueError("Should be otaku to call on_set_otaku()!")

        old_money = self.get_generated_value("resources")
        new_money = 5000

        money_diff = new_money - old_money
        # money check
        if app_data.app_character.statblock.cash + money_diff < 0:
            print("Not enough money to become an otaku!")
            return False
        app_data.app_character.statblock.add_cash(money_diff)

        # pin otaku to top
        magic_index = self.priority_order.index("magic")
        first_half = self.priority_order[:magic_index]
        last_half = self.priority_order[magic_index + 1:]
        self.priority_order = ["magic"] + first_half + last_half

        # call this to rename "magic" to "otaku" or vice versa
        self.fill_lists()

        return True

    def on_unset_otaku(self):
        if app_data.app_character.statblock.otaku:
            raise ValueError("Should not be otaku to call on_set_otaku()!")

        old_money = 5000
        new_money = self.get_generated_value("resources")

        # this should always add money, if it doesn't, something went horribly wrong
        money_diff = new_money - old_money
        app_data.app_character.statblock.add_cash(money_diff)

        # call this to rename "magic" to "otaku" or vice versa
        self.fill_lists()

        return True

    def get_otaku_complex_forms_resources(self):
        """Returns amount from resources, not multiplied by 50."""
        index = self.priority_order.index("resources")

        return 4 - index

    def serialize(self):
        return {"type": "priority",
                "data": self.priority_order,
                "purchased_magic_points": self.purchased_magic_points.get()}
