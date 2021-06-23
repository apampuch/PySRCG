from abc import ABC, abstractmethod


class GenMode(ABC):
    # static variable that should be set first thing to point to the frame to hold the UI elements
    gen_mode_frame = None

    def __init__(self):
        # print(app_data.app_character)
        pass

    @abstractmethod
    def setup_ui_elements(self):
        # clear old UI elements
        for child in GenMode.gen_mode_frame.winfo_children():
            child.destroy()

        # app_data.window.add(app_data.window.tabs()[0])

    @abstractmethod
    def serialize(self):
        pass

    @abstractmethod
    def update_karma_label(self, tab):
        pass

    @abstractmethod
    def get_generated_value(self, key):
        """
        This is used by priority mostly, you pass in a key and it gives you the value for the priority
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