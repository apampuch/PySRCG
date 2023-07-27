from abc import ABC

from src import app_data
from src.CharData.augment import Bioware
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab


class BiowareTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "BiowareTab", show_bioware_grades=True)

    @property
    def library_source(self):
        try:
            return app_data.game_data["Bioware"]
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.bioware

    def on_tree_item_click(self, event):
        super().on_tree_item_click(event)
        # check if we need to grey out grades or not
        if len(self.object_library.selection()) > 0:
            # only select the last one selected if we've selected multiple things
            selected = self.object_library.selection()[-1]

            if selected in self.tree_item_dict.keys():
                selected_item = self.tree_item_dict[selected]

                if "grade" in selected_item.properties:
                    self.bio_standard_radio.config(state="disabled")
                    self.bio_cultured_radio.config(state="disabled")
                else:
                    self.bio_standard_radio.config(state="normal")
                    self.bio_cultured_radio.config(state="normal")

    def buy_callback(self, selected: Bioware):
        # check if cultured, if not, add grade
        if "grade" not in selected.properties:
            selected.add_field("grade", str(self.bio_grade_var.get()))
            selected.properties["bio_index"] = self.calc_essence_index_cost(selected, selected.properties["grade"])
            selected.properties["cost"] = self.calc_yen_cost(selected, selected.properties["grade"])

        # TODO make it display an actual warning when above essence index and prevent at 9
        if selected.properties["bio_index"] <= self.statblock.raw_essence_index:
            # if we have enough money
            if app_data.pay_cash(selected.properties["cost"]):
                self.add_inv_item(selected)
                self.calculate_total()
            else:
                print("Not enough cash!")
        else:
            print("Not enough essence left!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock_inventory[self.inv_selected_index]

        # return cash value
        self.statblock.add_cash(selected_item.properties["cost"])

        self.remove_inv_item(self.inv_selected_index)

        self.calculate_total()

    @staticmethod
    def calc_essence_index_cost(bio, grade):
        bio_index = bio.properties["bio_index"]

        if grade == "standard":
            pass
        elif grade == "cultured":
            bio_index *= .75
        else:
            raise ValueError("Invalid grade {}.".format(grade))

        return bio_index

    @staticmethod
    def calc_yen_cost(bio, grade):
        cost = bio.properties["cost"]

        if grade == "standard":
            pass
        elif grade == "cultured":
            cost *= 4
        else:
            raise ValueError("Invalid grade {}.".format(grade))

        return cost

    @property
    def recurse_check_func(self):
        def bioware_tab_recurse_check(val):
            return "bio_index" not in val.keys()

        return bioware_tab_recurse_check

    @property
    def recurse_end_func(self):
        def bioware_tab_recurse_end_callback(key, val, iid):
            # key is a string
            # val is a _dict from a json
            try:
                self.tree_item_dict[iid] = Bioware(name=key, **val)
            except TypeError as e:
                print("Error with bioware {}:".format(key))
                print(e)
                print()

        return bioware_tab_recurse_end_callback

    def calculate_total(self):
        app_data.top_bar.update_karma_bar("{:.2f}".format(self.statblock.essence_index),
                                          self.statblock.essence + 3.0,  # max essence index
                                          "Augments Tab")

    def on_switch(self):
        self.calculate_total()

    def load_character(self):
        super().load_character()
        self.on_switch()
