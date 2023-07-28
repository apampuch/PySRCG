import abc

from src import app_data


class Tab(abc.ABC):
    """
    This basically just acts like an interface, mostly.
    Any tab should inherit from this class.
    """

    def update_karma_bar(self):
        """Handler for updating the karma bar. If not overridden, will set karma bar to blank."""
        app_data.top_bar.karma_fraction.set("")
        app_data.top_bar.karma_bar.configure(variable=0, maximum=10000)

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
