import abc
from tkinter import IntVar

from src import app_data


class Tab(abc.ABC):
    """
    This basically just acts like an interface, mostly.
    Any tab should inherit from this class.
    """

    __always_zero = None

    @staticmethod
    def setup_always_zero():
        Tab.__always_zero = IntVar(value=0)

    def update_karma_bar(self):
        """Handler for updating the karma bar. If not overridden, will set karma bar to blank."""
        app_data.top_bar.karma_fraction.set("")
        app_data.top_bar.karma_bar.configure(variable=Tab.__always_zero, maximum=1)

    @abc.abstractmethod
    def reload_data(self):
        """Called when data is loaded."""
        pass

    @abc.abstractmethod
    def on_switch(self):
        """Called on tab switch."""
        pass

    @abc.abstractmethod
    def load_character(self):
        """Called on character load."""
        pass
