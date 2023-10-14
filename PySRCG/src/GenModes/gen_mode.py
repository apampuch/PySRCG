from abc import ABC, abstractmethod
from typing import Literal

from src import app_data


class GenMode(ABC):
    # static variable that should be set first thing to point to the frame to hold the UI elements
    parent = None

    def __init__(self):
        self.karma_bar_vals = {}

    @staticmethod
    @abstractmethod
    def setup_ui_elements():
        pass

    @abstractmethod
    def grid_ui_elements(self):
        # clear old UI elements
        for child in GenMode.parent.gen_mode_frame.winfo_children():
            child.grid_forget()

        # app_data.window.add(app_data.window.tabs()[0])

    @abstractmethod
    def fill_valid_metatypes(self):
        """Fills parent.listbox"""
        GenMode.parent.metatype_listbox_values.clear()
        GenMode.parent.metatype_keys.clear()

    def on_change_to_genmode(self, old_money):
        """Must be called when changing from one genmode to another"""
        if not app_data.app_character.statblock.otaku:
            new_money = self.get_generated_value("resources")
            money_diff = new_money - old_money
            app_data.app_character.statblock.add_cash(money_diff)
            app_data.app_character.statblock.gen_mode.fill_valid_metatypes()

        # set combobox to correct metatype
        meta_name = app_data.app_character.statblock.metatype.name
        # only fix it if the metatype actually exists
        if meta_name in GenMode.parent.metatype_keys:
            meta_index = GenMode.parent.metatype_keys.index(meta_name)
            GenMode.parent.metatype_box.current(meta_index)

    @abstractmethod
    def serialize(self):
        pass

    @abstractmethod
    def get_generated_value(self, key: Literal["resources", "attributes", "metatype", "skills", "magic"]):
        """
        This is used by priority mostly, you pass in a key, and it gives you the value for the priority
        that that key is at.
        :param key:
        :return:
        """
        pass

    @abstractmethod
    def update_total(self, amount, key):
        """
        Needs to have the following keys:
        attributes
        skills
        magic
        """
        pass

    @abstractmethod
    def point_purchase_allowed(self, amount, key):
        """Amount is the total. Key is what you want to purchase."""
        pass

    @abstractmethod
    def on_metatype_selected(self):
        """Called by SetupTab when metatype is selected"""
        pass

    @abstractmethod
    def on_set_otaku(self) -> bool:
        """
        Called when setting otaku to True.
        Returns True if successful, False if not.
        """
        pass

    @abstractmethod
    def on_unset_otaku(self):
        """Undoes stuff from on_set_otaku()"""
        pass

    @abstractmethod
    def get_otaku_complex_forms_resources(self):
        """Gets the number of MP you have from resources / 50"""
        pass
