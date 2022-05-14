from abc import ABC

from tkinter import *

from src import app_data
from src.CharData.race import all_races
from src.GenModes.gen_mode import GenMode
from src.Tabs.Attributes.attributes_tab import AttributesTab
from src.Tabs.Augments.augments_tab import AugmentsTab
from src.Tabs.Background.background_tab import BackgroundTab
from src.Tabs.Background.edges_flaws_tab import EdgesFlawsTab
from src.Tabs.Decking.decking_tab import DeckingTab
from src.Tabs.Magic.magic_tab import MagicTab
from src.Tabs.Skills.skills_tab import SkillsTab
from src.utils import magic_tab_show_on_awakened_status


class Priority(GenMode, ABC):
    def __init__(self, priority_order=None, race=None):
        super().__init__()
        self.starting_skills_max = 6

        # 0 is highest priority, 4 is lowest
        if priority_order is None:
            self.priority_order = ["resources", "attributes", "race", "skills", "magic"]
        else:
            self.priority_order = priority_order

        # this _dict corresponds to the value of the priority of each option
        # e.g. magic C would be priority_value_dict["magic"][2]
        self.priority_value_dict = {
            "resources": [1000000, 400000, 90000, 20000, 5000],
            "attributes": [30, 27, 24, 21, 18],
            "race": [["Elf", "Troll", "Dwarf", "Ork", "Human"],
                     ["Elf", "Troll", "Dwarf", "Ork", "Human"],
                     ["Elf", "Troll", "Dwarf", "Ork", "Human"],
                     ["Dwarf", "Ork", "Human"],
                     ["Human"]],
            "skills": [50, 40, 34, 30, 27],
            "magic": ["Full", "Aspected", None, None, None]
        }

        # this is a shit way of doing it but I have no choice
        # these need to have their values assigned after I make all of the tabs
        self.priority_name_list = None
        self.priority_vals_list = None
        self.up_button = None
        self.down_button = None

        self.cur_skill_points = IntVar()
        self.cur_magic_points = IntVar()
        self.cur_attribute_points = IntVar()
        self.cur_edge_flaw_points = IntVar()

        self.max_skill_points = IntVar()
        self.max_magic_points = IntVar()
        self.max_attribute_points = IntVar()

        self.max_skill_points.set(self.get_generated_value("skills"))
        self.max_magic_points.set(self.magic_val_from_string())
        self.max_attribute_points.set(self.get_generated_value("attributes"))

        # after instantiating call AttributesTab.calculate_total

    def point_purchase_allowed(self, amount: int, key: str) -> bool:
        threshold = 0
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

    def update_karma_label(self, tab):
        """
        Updates the top bar's Karma label. Usually called when switching tabs.
        This is what controls what the top bar shows.
        """
        progress_text = app_data.top_bar.karma_fraction
        progress_bar = app_data.top_bar.karma_bar

        def blank_set():
            progress_text.set("")
            progress_bar.configure(maximum=10000000, variable=0)

        if type(tab) is AttributesTab:
            progress_text.set("{}/{}".format(self.cur_attribute_points.get(), self.max_attribute_points.get()))
            progress_bar.configure(maximum=self.max_attribute_points.get(), variable=self.cur_attribute_points)
        elif type(tab) is MagicTab:
            # if magic tab check the sub tab
            # noinspection PyPep8Naming
            SPELLS_TAB_INDEX = 0
            POWERS_TAB_INDEX = 1
            current_tab_index = tab.index("current")
            if current_tab_index == SPELLS_TAB_INDEX:
                progress_text.set("{}/{}".format(self.cur_magic_points.get(), self.max_magic_points.get()))
                progress_bar.configure(maximum=self.max_magic_points.get(), variable=self.cur_magic_points)
            elif current_tab_index == POWERS_TAB_INDEX:
                points_cur = app_data.app_character.statblock.power_points
                points_max = app_data.app_character.statblock.magic + app_data.app_character.statblock.bonus_power_points
                progress_text.set("{}/{}".format(points_cur, points_max))
                progress_bar.configure(maximum=points_max,
                                       variable=app_data.app_character.statblock.power_points_ui_var)
        elif type(tab) is SkillsTab:
            progress_text.set("{}/{}".format(self.cur_skill_points.get(), self.max_skill_points.get()))
            progress_bar.configure(maximum=self.max_skill_points.get(), variable=self.cur_skill_points)
        elif type(tab) is AugmentsTab:
            # hacky scope breaking bullshit, refactor this whole damn function to not be in the character gen modes
            ess_amt = app_data.app_character.statblock.essence
            ess_max = app_data.app_character.statblock.base_attributes["essence"]
            progress_text.set("{}/{}".format(ess_amt, ess_max))
            progress_bar.configure(maximum=ess_max, variable=app_data.app_character.statblock.ess_ui_var)
        elif type(tab) is DeckingTab:
            PERSONA_TAB_INDEX = 2
            current_tab_index = tab.index("current")
            if current_tab_index != PERSONA_TAB_INDEX:
                blank_set()
        elif type(tab) is BackgroundTab:
            EDGES_FLAWS_INDEX = 1
            current_tab_index = tab.index("current")
            if current_tab_index == EDGES_FLAWS_INDEX:
                progress_text.set("{}".format(self.cur_edge_flaw_points.get()))
                progress_bar.configure(maximum=10000000, variable=0)
        else:
            blank_set()

        # TODO check if we're over the maximum, if so, change to red
        # if not, change to green
        # need styles to do this

    def setup_ui_elements(self):
        super().setup_ui_elements()

        self.up_button = Button(GenMode.gen_mode_frame, text="↑", command=lambda: self.swap_priority(-1))
        self.down_button = Button(GenMode.gen_mode_frame, text="↓", command=lambda: self.swap_priority(1))

        self.priority_name_list = Listbox(GenMode.gen_mode_frame, height=5, selectmode=SINGLE, exportselection=0)
        self.priority_name_list.bind("<<ListboxSelect>>", self.sync_list_selected)
        self.priority_vals_list = Listbox(GenMode.gen_mode_frame, height=5, selectmode=SINGLE, exportselection=0)
        self.priority_vals_list.bind("<<ListboxSelect>>", self.sync_list_selected)

        self.up_button.grid(column=2, row=1)
        self.down_button.grid(column=2, row=2)
        self.priority_name_list.grid(column=0, row=1, columnspan=2, rowspan=2)
        self.priority_vals_list.grid(column=3, row=1, columnspan=2, rowspan=2)

        self.fill_lists()

    def update_total(self, amount, key):
        if key is "attributes":
            self.cur_attribute_points.set(amount)
            app_data.top_bar.update_karma_bar(self.cur_attribute_points.get(),
                                              self.max_attribute_points.get(),
                                              "Priority Mode")

        elif key is "skills":
            self.cur_skill_points.set(amount)
            app_data.top_bar.update_karma_bar(self.cur_skill_points.get(),
                                              self.max_skill_points.get(),
                                              "Priority Mode")
        elif key is "magic":
            self.cur_magic_points.set(amount)
            app_data.top_bar.update_karma_bar(self.cur_magic_points.get(),
                                              self.max_magic_points.get(),
                                              "Priority Mode")

    def swap_priority(self, direction):
        # do nothing if nothing is selected
        if len(self.priority_name_list.curselection()) is 0:
            return

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

        self.on_priority_change(old_money)

    # gets the magic point value from a string like Full or Aspected
    def magic_val_from_string(self):
        awakened_type = self.get_generated_value("magic")
        if awakened_type is "Full":
            return 25
        elif awakened_type is "Aspected":
            return 35
        else:
            return 0

    def on_priority_change(self, old_money):
        """set old values to new ones"""
        self.max_attribute_points.set(self.get_generated_value("attributes"))
        self.max_magic_points.set(self.magic_val_from_string())
        self.max_skill_points.set(self.get_generated_value("skills"))

        # breaking scope like this is SO hacky but fuck it
        # set money
        money_diff = self.get_generated_value("resources") - old_money
        # app_data.app_character.statblock.cash += money_diff
        app_data.app_character.statblock.add_cash(money_diff)

        # reset to human if race isn't valid
        if app_data.app_character.statblock.race.name not in self.get_generated_value("race"):
            app_data.app_character.statblock.race = all_races["Human"]

        # set magic
        awakened_val = self.get_generated_value("magic")
        app_data.app_character.statblock.awakened = awakened_val
        # set aspect to Full Mage if magic is top priority
        if awakened_val == "Full":
            app_data.app_character.statblock.aspect = "Full Mage"

        app_data.app_character.statblock.awakened = awakened_val

        magic_tab_show_on_awakened_status(app_data)

    def sync_list_selected(self, event):
        # figure out which we clicked
        if event.widget is self.priority_name_list:
            clicked_widget = self.priority_name_list
            syncing_widget = self.priority_vals_list
        else:
            clicked_widget = self.priority_vals_list
            syncing_widget = self.priority_name_list

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
            self.priority_name_list.insert(END, self.priority_order[i])
            self.priority_vals_list.insert(END, L[i])

    def serialize(self):
        return {"type": "priority", "data": self.priority_order}

    def pretty_priority_values(self):
        L = self.priority_values()

        # find cash
        cash_index = self.priority_order.index("resources")
        L[cash_index] = "¥" + str(L[cash_index])
        # find race
        race_index = self.priority_order.index("race")
        if race_index is 4:
            L[race_index] = "Human"
        elif race_index is 3:
            L[race_index] = "Dwarf/Ork"
        elif race_index is 2:
            L[race_index] = "Elf/Troll"
        else:
            L[race_index] = "Any Race"
        # find magic
        magic_index = self.priority_order.index("magic")
        if magic_index is 0:
            L[magic_index] = "Full Mage"
        elif magic_index is 1:
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
