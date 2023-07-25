from abc import ABC
from copy import copy
from tkinter.ttk import Labelframe

from src import app_data
from src.CharData.complex_form import ComplexForm
from src.CharData.skill import Skill
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


# should be hidden if character is not an otaku
class ComplexFormsTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "ComplexFormsTab")

    @property
    def library_source(self):
        try:
            # no operational utilities because Otaku don't use them
            d = copy(self.parent.game_data["Programs"])
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
        print(f"{self.complex_forms_mp_total()}/{self.complex_forms_mp_limit()}")

        if self.complex_forms_mp_total() + selected.size() <= self.complex_forms_mp_limit():
            self.add_inv_item(selected)
        else:
            print("Not enough space!")

    def sell_callback(self, selected_index):
        self.remove_inv_item(selected_index)

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
        app_data.top_bar.update_karma_bar(self.complex_forms_mp_total(),
                                          self.complex_forms_mp_limit(),
                                          "Complex Forms Tab")

    def on_switch(self):
        self.calculate_total()

    def load_character(self):
        self.on_switch()
