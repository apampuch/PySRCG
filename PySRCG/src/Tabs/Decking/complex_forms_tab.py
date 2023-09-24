from abc import ABC
from copy import copy
from tkinter import IntVar

from src import app_data
from src.CharData.complex_form import ComplexForm
from src.CharData.skill import Skill
from src.GenModes.finalized import Finalized
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


# should be hidden if character is not an otaku
from src.adjustment import Adjustment


class ComplexFormsTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "ComplexFormsTab")

        self.forms_total = IntVar()

    @property
    def library_source(self):
        try:
            # no operational utilities because Otaku don't use them
            d = copy(app_data.game_data["Programs"])
            del d["Operational Utilities"]
            return d
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.complex_forms

    def complex_forms_mp_limit(self):
        resources = self.gen_mode.get_otaku_complex_forms_resources()

        programming = 0

        # find the computer skill if it exists
        computer: Skill | None
        computer = None
        for skill in self.statblock.skills:
            if skill.name == "Computer":
                computer = skill
                break

        if computer is not None:
            # set programming to computer skill
            programming = computer.rank
            # check if we have programming specialization or not
            # set if we do
            for spec in computer.specializations:
                if spec.name == "Programming":
                    programming = spec.rank

        return (resources + programming) * 50

    def complex_forms_mp_total(self):
        total = 0

        for item in self.statblock_inventory:
            total += item.size()

        return total

    def buy_callback(self, selected):
        if type(self.gen_mode) is not Finalized:
            if self.complex_forms_mp_total() + selected.size() <= self.complex_forms_mp_limit():
                self.add_inv_item(selected)
                self.forms_total.set(self.complex_forms_mp_total())
                self.calculate_total()
            else:
                print("Not enough space!")
        # if finalized it's just 1 karma
        else:
            if self.gen_mode.point_purchase_allowed(1, None):
                self.add_inv_item(selected)

                def undo():
                    return
                adjustment = Adjustment(1, "add_complex_form_" + selected.properties["name"], undo, "Add complex form")
                self.gen_mode.add_adjustment(adjustment)

                self.calculate_total()
            else:
                print("Not enough karma!")

    def sell_callback(self, selected_index):
        selected_form = self.statblock.complex_forms[self.inv_selected_index]

        # TODO make this account for options and rating
        if type(self.gen_mode) == Finalized:
            if "add_complex_form_" + selected_form.properties["name"] in self.gen_mode.adjustments:
                self.gen_mode.undo("add_complex_form_" + selected_form.properties["name"])
                self.remove_inv_item(self.inv_selected_index)
        else:
            self.remove_inv_item(selected_index)
            self.forms_total.set(self.complex_forms_mp_total())
            self.calculate_total()

    @property
    def recurse_check_func(self):
        def complex_forms_tab_recurse_check(val):
            return "multiplier" not in val.keys()

        return complex_forms_tab_recurse_check

    @property
    def recurse_end_func(self):
        def complex_forms_tab_recurse_end_callback(key, val, iid):
            self.tree_item_dict[iid] = ComplexForm(name=key, **val)

        return complex_forms_tab_recurse_end_callback

    def calculate_total(self):
        if type(self.gen_mode) is not Finalized:
            app_data.top_bar.update_karma_label(self.complex_forms_mp_total(),
                                                self.complex_forms_mp_limit(),
                                                "Complex Forms Tab")
        else:
            self.gen_mode.update_total(None, None)

    def update_karma_bar(self):
        progress_bar = app_data.top_bar.karma_bar
        if type(self.gen_mode) is not Finalized:
            self.forms_total.set(self.complex_forms_mp_total())
            progress_bar.configure(variable=self.forms_total, maximum=self.complex_forms_mp_limit())
        else:
            progress_bar.configure(variable=self.gen_mode.adjustments, maximum=self.gen_mode.good_karma.get())

    def on_switch(self):
        super().on_switch()
        self.calculate_total()

    def load_character(self):
        super().load_character()
