from copy import copy
from math import floor
from tkinter import *
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

from src.CharData.skill import Skill, Specialization
from src.GenModes.finalized import Finalized
from src.adjustment import Adjustment
from src.utils import treeview_get, recursive_treeview_fill
from src.Tabs.notebook_tab import NotebookTab


class SkillsTab(NotebookTab):
    tree_library_dict: Dict[str, tuple]
    tree_list_dict: Dict[str, Skill]  # or str, Specialization

    @property
    def library_selected(self):
        return treeview_get(self.object_library, self.tree_library_dict)

    @property
    def list_selected(self) -> Skill:
        return treeview_get(self.skills_list, self.tree_list_dict, make_copy=False)

    def __init__(self, parent):
        super().__init__(parent, "SkillsTab")
        # TODO add an implementation of no_duplicates

        self.tree_library_dict = {}  # maps library terminal children iids to (skill name, skill attribute) tuple
        self.tree_list_dict = {}  # same but for player skills AND specializations
        # self.tree_spec_dict = {}  # specializations of each skill (iid, specialization name)

        # frame to hold the list of skills
        self.object_library = ttk.Treeview(self, height=20, show="tree")
        self.skills_library_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.object_library.yview)

        # frame to hold the player's skills
        self.skills_list = ttk.Treeview(self, height=20, columns=["Rank", "Attribute"])
        self.skills_list.heading("#0", text="Skill")
        self.skills_list.heading("#1", text="Rank")
        self.skills_list.heading("#2", text="Attribute")
        self.skills_list.column("#1", width=60)
        self.skills_list.column("#2", width=120)
        self.skills_list_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.skills_list.yview)

        # buttons
        self.add_button = Button(self, text="Add", command=self.add_skill)
        self.remove_button = Button(self, text="Remove", command=self.remove_skill)
        self.specialize_button = Button(self, text="Specialize", command=self.specialize_skill)
        self.plus_button = Button(self, text="+", command=self.plus_skill)
        self.minus_button = Button(self, text="-", command=self.minus_skill)

        # bind events
        self.object_library["yscrollcommand"] = self.skills_library_scroll.set
        self.skills_list["yscrollcommand"] = self.skills_list_scroll.set

        # grids
        self.object_library.grid(column=0, row=0, sticky=(N, S), columnspan=2)
        self.skills_library_scroll.grid(column=2, row=0, sticky=(N, S))

        self.skills_list.grid(column=4, row=0, sticky=(N, S), columnspan=3)
        self.skills_list_scroll.grid(column=7, row=0, sticky=(N, S))

        self.add_button.grid(column=0, row=1)
        self.remove_button.grid(column=1, row=1)
        self.specialize_button.grid(column=4, row=1)
        self.plus_button.grid(column=5, row=1)
        self.minus_button.grid(column=6, row=1)

        # fill skills library
        recursive_treeview_fill(self.library_source, "", self.object_library,
                                self.recurse_check_func, self.recurse_end_func)

    @property
    def recurse_check_func(self):
        def skills_tab_recurse_check(val):
            return "attribute" not in val.keys()

        return skills_tab_recurse_check

    @property
    def recurse_end_func(self):
        def skills_tab_recurse_end_callback(key, val, iid):
            # rank is 0 since it's not real in the library
            self.tree_library_dict[iid] = Skill(name=key, rank=0, **val)
            self.object_library.item(iid, text="{} ({})".format(key, val))

        return skills_tab_recurse_end_callback

    @property
    def library_source(self):
        try:
            return self.parent.game_data["Skills"]
        except KeyError:
            return {}

    def add_skill(self):
        if self.library_selected is not None:
            if type(self.gen_mode) == Finalized:
                skills_total = 1
            else:
                skills_total = self.get_total()

            # disallow duplicates
            for skill in self.statblock.skills:
                if skill.name == self.library_selected.name:
                    messagebox.showerror(title="Error", message="No duplicate skills allowed.")
                    return

            if self.gen_mode.point_purchase_allowed(skills_total, "skills"):
                # make a skill object, then add to the player's skills treeview, then hook them together
                # in tree_list_dict

                new_skill: Skill = copy(self.library_selected)
                new_skill.rank += 1
                self.statblock.skills.append(new_skill)
                new_skill_iid = self.insert_skill(new_skill)

                if type(self.gen_mode) == Finalized:
                    def undo():
                        """Deletes from the skills list with the associated iid this was created with."""
                        self.skills_list.delete(new_skill_iid)

                    adjustment = Adjustment(1, "add_skill_" + new_skill.name, undo, "Add new skill")
                    self.gen_mode.add_adjustment(adjustment)

                self.calculate_total()
            else:
                print("Not enough points!")
        else:
            print("Can't add that!")

    def insert_skill(self, skill):
        # add to tree
        iid = self.skills_list.insert("", "end", text=skill.name,
                                      values=(skill.rank, skill.attribute))

        self.tree_list_dict[iid] = skill

        # add child specializations
        for spec in skill.specializations:
            # make the child of the skill tree item
            s_iid = self.skills_list.insert(iid, "end", text=spec,
                                            value=skill.specializations[spec] + skill.rank)
            # add it to the dictionary mapping the id to spec name
            self.tree_list_dict[s_iid] = spec
            # self.tree_spec_dict[iid][s_iid] = spec

        # returns the iid so that we can make an undo function with it
        return iid

    def remove_skill(self):
        # don't do anything if nothing is selected
        if len(self.skills_list.selection()) is 0:
            return

        selected_list_item_iid = self.skills_list.selection()[-1]  # this is an iid
        parent_ui_item_iid = self.skills_list.parent(selected_list_item_iid)

        # if we're finalized, check if the remove is valid
        if type(self.gen_mode) == Finalized:
            # get the skill object from the iid
            skill = self.tree_list_dict[selected_list_item_iid]

            # if a specialization, just remove that
            if type(skill) == Specialization:
                # check if we added the specialization during this round of adjustments
                # if so, undo the add
                if self.gen_mode.remove_by_adjustment_type(skill, "add_spec_", "increase_spec_"):
                    self.gen_mode.undo("add_spec_" + skill.name)
                else:
                    print("Can't remove that specialization!")

            # otherwise, remove all of the specializations and the skill itself
            else:
                # check if we added the skill during this round of adjustments
                # if so, undo the add
                if self.gen_mode.remove_by_adjustment_type(skill, "add_skill_", "increase_skill_"):
                    for spec in skill.specializations:
                        # this is just to check for bugs, we SHOULD always have an add_spec_ where we have an add_skill_
                        if self.gen_mode.remove_by_adjustment_type(spec, "add_spec_", "increase_spec_"):
                            self.gen_mode.undo("add_spec_" + skill.name)
                        else:
                            print("ERROR: Add spec does not exist where we created a skill.")
                    self.gen_mode.undo("add_skill_" + skill.name)
                else:
                    print("Can't remove that skill!")

        # otherwise try this for every other gen mode
        else:
            # if the parent item is not "", it's a specialization, and we need to only remove it from its skill
            if parent_ui_item_iid is not "":
                # get the parent skill
                parent_item = self.tree_list_dict[parent_ui_item_iid]
                ui_name = self.skills_list.item(self.selected_skill_ui_iid(), "text")
                # find the specialization itself and remove it
                for spec in parent_item.specializations:
                    if spec.name == ui_name:
                        parent_item.specializations.remove(spec)
                # increase the rank and update the UI
                parent_item.rank += 1
                self.skills_list.item(parent_ui_item_iid, value=(parent_item.rank, parent_item.attribute))
            # otherwise it's a skill and we need to remove all of its children (specializations) too
            else:
                skill = self.tree_list_dict[selected_list_item_iid]
                self.statblock.skills.remove(skill)

                # swear to god this line used to work?
                # for spec_ui_item in self.skills_list[selected_list_item_iid].children():
                for spec_ui_item in self.skills_list.get_children(selected_list_item_iid):
                    self.skills_list.delete(spec_ui_item)
                del self.tree_list_dict[selected_list_item_iid]
            # either way, delete the thing we're trying to delete
            self.skills_list.delete(selected_list_item_iid)

        # calculate the total no matter what
        self.calculate_total()

    def specialize_skill(self):
        # TODO make it limit the number of specializations to the linked attribute
        # don't do anything if nothing is selected
        if len(self.skills_list.selection()) is 0:
            return

        # only make these checks if we're not finalized
        if type(self.gen_mode) is not Finalized:
            # don't do it if the skill is 1 or less
            if self.list_selected.rank is 1:
                print("Too low to specialize")
                return

            # don't do it if we're already specialized
            if len(self.list_selected.specializations) > 0:
                messagebox.showerror(title="Error", message="Already specialized.")
                return
        # check if we have enough karma if we're finalized
        else:
            spec_cost = self.skill_improve_cost_calc(self.list_selected)
            if not self.gen_mode.point_purchase_allowed(spec_cost, None):
                print("Not enough karma!")
                return

        # setup new window
        temp_window = Toplevel(self.parent)
        temp_window.grab_set()
        temp_window.resizable(0, 0)

        name_entry = Entry(temp_window)

        # funcs that we give to the buttons in the temp window
        def ok_func():
            if name_entry.get() is not "":
                # make a new item in the UI with the value equal to 1 plus the current rank
                new_item_iid = self.skills_list.insert(self.selected_skill_ui_iid(), "end", text=name_entry.get(),
                                                       value=self.list_selected.rank + 1)
                # if we aren't finalized, decrease the rank by 1 and set the specialization value to 2 plus rank
                if type(self.gen_mode) is not Finalized:
                    self.list_selected.rank -= 1
                    new_spec = Specialization(name_entry.get(), self.list_selected.rank + 2,
                                              self.list_selected.attribute)
                    self.list_selected.specializations.append(new_spec)
                    # self.list_selected_skill.specializations[name_entry.get()] = 2
                # if we are finalized, set specialization value to 1
                else:
                    new_spec = Specialization(name_entry.get(), self.list_selected.rank + 1,
                                              self.list_selected.attribute)
                    self.list_selected.specializations.append(new_spec)
                    # self.list_selected_skill.specializations[name_entry.get()] = 1

                # update the parent skill in the UI
                self.skills_list.item(self.selected_skill_ui_iid(), value=(self.list_selected.rank,
                                                                           self.list_selected.attribute))
                self.tree_list_dict[new_item_iid] = new_spec
                # self.tree_spec_dict[selected][new_item] = name_entry.get()
                temp_window.destroy()

        def cancel_func():
            temp_window.destroy()

        Label(temp_window, text="Specialization:").pack()
        name_entry.pack(fill=X)
        Button(temp_window, text="OK", command=ok_func).pack(side=LEFT)
        Button(temp_window, text="Cancel", command=cancel_func).pack(side=RIGHT)

    def plus_skill(self):
        # don't do anything if nothing is selected
        if len(self.skills_list.selection()) is 0:
            return

        # figure out if finalized or not
        if type(self.gen_mode) is Finalized:
            # calculate the karma cost
            karma_cost = self.skill_improve_cost_calc(self.list_selected)
            if self.gen_mode.point_purchase_allowed(karma_cost, "skills"):
                self.list_selected.rank += 1

                # undo function
                def undo():
                    self.list_selected.rank -= 1

                # set the increase prefix based on if it's a specialization or not
                increase_prefix = "increase_spec" if type(self.list_selected) == Specialization else "increase_skill_"

                adjustment = Adjustment(karma_cost, increase_prefix + self.list_selected.name, undo)
                self.gen_mode.add_adjustment(adjustment)
        else:
            # check if we're a specialization or not and do nothing if we're not
            if type(self.list_selected) == Specialization:
                print("Can't change a specialization's rank until finalized!")
                return

            # we do this part here so the following doesn't happen
            # e.g. pistols 3, quickness 3, 26/27 pts, increasing to pistols 4
            # would give 28/27
            test_val = self.get_total()
            if self.list_selected.rank >= self.statblock.calculate_natural_attribute(self.list_selected.attribute):
                test_val += 1

            # increase rank if allowed
            final_starting_max_value = (self.gen_mode.starting_skills_max - 1) \
                if len(self.list_selected.specializations) > 0 \
                else self.gen_mode.starting_skills_max
            # check that we have enough points and aren't going past the max
            if self.list_selected is not None and \
                    self.gen_mode.point_purchase_allowed(test_val, "skills") and \
                    self.list_selected.rank < final_starting_max_value:

                self.list_selected.rank += 1
                # how do I link the child UI items to the specializations?
                for spec in self.list_selected.specializations:
                    spec.rank += 1
                for spec_ui_iid in self.skills_list.get_children(self.selected_skill_ui_iid()):
                    spec_rank = int(self.skills_list.item(spec_ui_iid)["values"][0])  # convert first value to int
                    self.skills_list.item(spec_ui_iid, value=spec_rank + 1)  # set new value in UI

        # update the value in the ui
        self.skills_list.item(self.selected_skill_ui_iid(),
                              value=(self.list_selected.rank, self.list_selected.attribute))

        # calculate total no matter what
        self.calculate_total()

    def minus_skill(self):
        # don't do anything if nothing is selected
        if len(self.skills_list.selection()) is 0:
            return

        if type(self.gen_mode) is Finalized:
            # increase_ and increase_spec_ are different because 
            # we may need to remove a specialization that has the same name as a skill
            undo_prefix = "increase_spec_" if type(self.list_selected) == Specialization else "increase_skill_"
            undo_type = undo_prefix + self.list_selected.name
            self.statblock.gen_mode.undo(undo_type)
            self.skills_list.item(self.selected_skill_ui_iid(),
                                  value=(self.list_selected.rank, self.list_selected.attribute))
        else:
            # check if we're a specialization or not
            if type(self.list_selected) == Specialization:
                print("Can't change a specialization's rank until finalized!")
                return

            # check that we're not decreasing below the minimum
            if self.list_selected is not None and self.list_selected.rank > 1:
                # decrease rank, reflect change in UI and in list
                self.list_selected.rank -= 1

                # decrease rank of specializations
                for spec in self.list_selected.specializations:
                    spec.rank -= 1

                # update specializations
                for spec_ui_iid in self.skills_list.get_children(self.selected_skill_ui_iid()):
                    spec_rank = int(self.skills_list.item(spec_ui_iid)["values"][0])  # convert first value to int
                    self.skills_list.item(spec_ui_iid, value=spec_rank - 1)  # set new value in UI

                self.skills_list.item(self.selected_skill_ui_iid(),
                                      value=(self.list_selected.rank, self.list_selected.attribute))

        # calculate total no matter what
        self.calculate_total()

    def skill_improve_cost_calc(self, skill) -> int:
        """
        Calculates karma cost of skill improvement based on p245 of SR3 core book.
        :param skill: Skill or specialization we're improving.
        :return: Karma cost of skill.
        """

        new_rating = skill.rank + 1
        linked_attribute = self.statblock.calculate_natural_attribute(self.list_selected.attribute)

        if type(skill) == Skill:
            if skill.skill_type == "active":
                if new_rating <= linked_attribute:
                    return floor(new_rating * 1.5)
                elif new_rating <= linked_attribute * 2:
                    return floor(new_rating * 2)
                else:
                    return floor(new_rating * 2.5)
            else:
                if new_rating <= linked_attribute:
                    return floor(new_rating * 1)
                elif new_rating <= linked_attribute * 2:
                    return floor(new_rating * 1.5)
                else:
                    return floor(new_rating * 2)
        elif type(skill) == Specialization:
            if linked_attribute is None:
                raise ValueError("Linked attribute for a specialization must be given as a number.")
            if new_rating <= linked_attribute:
                return floor(new_rating * .5)
            elif new_rating <= linked_attribute * 2:
                return floor(new_rating * 1)
            else:
                return floor(new_rating * 1.5)
        else:
            print("Given skill is neither a skill nor a specialization.")

    def get_total(self):
        """Totals all skill points and updates the top karma bar."""
        total = 0

        # calculate the total
        for skill in self.tree_list_dict.values():
            # skip it if we're not a skill, this is so we don't count specializations
            if type(skill) is not Skill:
                continue

            # adjust the rank total for skills that have specializations
            # they should count as their unspecialized rank for this purpose
            rank_total = skill.rank
            if len(skill.specializations) > 0:
                rank_total += 1

            pre_points = min(rank_total, self.statblock.calculate_natural_attribute(skill.attribute))
            post_points = max(0, rank_total - self.statblock.calculate_natural_attribute(skill.attribute)) * 2
            total += pre_points + post_points

        return total

    def calculate_total(self):
        self.statblock.gen_mode.update_total(self.get_total(), "skills")

    def on_library_item_click(self, event):
        pass

    def on_list_item_click(self, event):
        pass

    def selected_skill_ui_iid(self):
        """
        :return: The iid of the selected skill UI item
        """
        return self.skills_list.selection()[-1]

    def reload_data(self):
        children = self.object_library.get_children()
        self.object_library.delete(*children)
        recursive_treeview_fill(self.library_source, "", self.object_library,
                                self.recurse_check_func, self.recurse_end_func)

    def load_character(self):
        # clear everything
        self.tree_list_dict = {}
        self.skills_list.delete(*self.skills_list.get_children())

        for skill in self.statblock.skills:
            self.insert_skill(skill)

        self.on_switch()

    def on_switch(self):
        self.calculate_total()
