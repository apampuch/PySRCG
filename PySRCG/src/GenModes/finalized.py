from abc import ABC
from tkinter import IntVar

from src import app_data
from src.GenModes.gen_mode import GenMode
from src.Tabs.Rigging.vehicle_accessories_tab import VehicleAccessoriesTab
from src.Tabs.Rigging.vehicle_buy_tab import VehicleBuyTab
from src.adjustment import AdjustmentsContainer, Adjustment


class Finalized(GenMode, ABC):
    """
    The "genmode" used for after a character is finalized.
    Assume that a character's karma is unspent until spent.
    """

    adjustments: AdjustmentsContainer

    def __init__(self, data=None, race=None):
        super().__init__()

        self.starting_skills_max = 99   # why you'd ever need more than 100 dice idk
        self.good_karma = IntVar()      # don't set directly, use self.set_total_karma
        self.karma_pool = IntVar()      # never set directly, only use set_total_karma
        self.applied_karma = IntVar()   # applied karma is the amount of karma spent from applied changes
        self.karma_pool.set(1)          # yes we're setting it here, don't get smart with me

        if data is not None and race is not None:
            self.set_total_karma(data["total_karma"], race)
            self.applied_karma.set(data["applied_karma"])

        self.adjustments = AdjustmentsContainer()

    def total_karma(self):
        """
        Returns total karma, good karma plus karma pool.
        The -1 is to offset the one free karma pool.
        :return: Good karma + karma pool.
        """
        return self.karma_pool.get() + self.good_karma.get() - 1

    def add_karma(self, amount, race):
        """
        Adds karma to the total.
        :param amount: Amount of good karma to add.
        :param race: Race of the character. This matters due to humans getting more Karma Pool.
        """
        total = self.total_karma() + amount
        self.set_total_karma(total, race)

    def sub_karma(self, amount, race):
        """
        Subtracts karma to the total. Won't go below 0.
        :param amount: Amount of good karma to subtract.
        :param race: Race of the character. This matters due to humans getting more Karma Pool.
        """
        total = max(self.total_karma() - amount, self.spent_karma)  # so we don't go below 0
        self.set_total_karma(total, race)

    # calculates good karma and subtracts the karma pool tax
    def set_total_karma(self, total, race):
        self.karma_pool.set(total // race.karma_div + 1)         # +1 because you start with 1 karma pool
        good_karma_set = total - self.karma_pool.get()
        self.good_karma.set(good_karma_set + 1)  # +1 because you start with that karma pool for free

    def get_generated_value(self, key):
        pass

    def setup_ui_elements(self):
        super().setup_ui_elements()

        # test this
        app_data.window.hide(app_data.window.tabs()[0])

    def serialize(self):
        return {"type": "finalized",
                "data": {"total_karma": self.total_karma(),
                         "applied_karma": self.applied_karma.get()}}

    def update_karma_label(self, tab):
        progress_text = app_data.top_bar.karma_fraction
        progress_bar = app_data.top_bar.karma_bar

        def blank_set():
            progress_text.set("")
            progress_bar.configure(maximum=10000000, variable=0)

        # do these imports here to avoid circular import bullshit
        from src.Tabs.Augments.augments_tab import AugmentsTab
        from src.Tabs.Background.personal_info_tab import PersonalInfoTab
        from src.Tabs.Decking.decking_tab import DeckingTab
        from src.Tabs.Gear.items_tab import ItemsTab
        from src.Tabs.Rigging.rigging_tab import RiggingTab
        from src.Tabs.Setup.setup_tab import SetupTab
        from src.Tabs.Magic.magic_tab import MagicTab

        # list of types of tabs that should be set the top bar to blank
        blank_set_types = (ItemsTab, SetupTab, PersonalInfoTab, DeckingTab, VehicleBuyTab, VehicleAccessoriesTab)

        if type(tab) in blank_set_types:
            blank_set()
        elif type(tab) is AugmentsTab:
            # hacky scope breaking bullshit, refactor this whole damn function to not be in the character gen modes
            ess_amt = app_data.app_character.statblock.essence
            ess_max = app_data.app_character.statblock.base_attributes["essence"]
            progress_text.set("{}/{}".format(ess_amt, ess_max))
            progress_bar.configure(maximum=ess_max, variable=app_data.app_character.statblock.ess_ui_var)
        elif type(tab) is MagicTab:
            # if magic tab check the sub tab
            # noinspection PyPep8Naming
            SPELLS_TAB_INDEX = 0
            POWERS_TAB_INDEX = 1
            current_tab_index = tab.index("current")
            if current_tab_index == SPELLS_TAB_INDEX:
                progress_text.set("{}/{}".format(self.spent_karma, self.good_karma.get()))
                progress_bar.configure(variable=self.adjustments, maximum=self.good_karma.get())
            elif current_tab_index == POWERS_TAB_INDEX:
                points_cur = app_data.app_character.statblock.power_points
                points_max = app_data.app_character.statblock.magic + app_data.app_character.statblock.bonus_power_points
                progress_text.set("{}/{}".format(points_cur, points_max))
        else:
            progress_text.set("{}/{}".format(self.spent_karma, self.good_karma.get()))
            progress_bar.configure(variable=self.adjustments, maximum=self.good_karma.get())

    def update_total(self, amount=None, key=None):  # set defaults here so we can call without args
        # Literally ignore everything and just refresh the karma bar.
        app_data.top_bar.update_karma_bar(self.spent_karma,
                                          self.good_karma.get(),
                                          "Finalized Mode")

    def add_adjustment(self, adj):
        """
        Adds the adjustment. THIS IS NOT SETTING THE TOTAL LIKE IN OTHER GEN MODES.
        :type adj: Adjustment
        :return: nothing
        :param adj:  An Adjustment, NOT an integer.
        :return: None
        """
        self.adjustments.add(adj)
        self.update_total()

    def remove_by_adjustment_type(self, obj, add_prefix, increase_prefix):
        """
        Used only by the Finalized gen type.
        See if we have anything by the name of add_ASDF in our adjustments.
        If we do, undo all of the increases then remove the skill and return True.
        Otherwise, do nothing and return False.
        :param obj: Object we're trying to remove.
        :param add_prefix: Prefix of the add adjustment to remove.
        :param increase_prefix: Prefix of the increase adjustment to remove.
        :return: If we should do the remove or not.
        """
        add_type = add_prefix + obj.name
        add_type_exists = add_type in self.adjustments
        if add_type_exists:
            increase_type = increase_prefix + obj.name
            while increase_type in self.adjustments:
                self.undo(increase_type)

        return add_type_exists

    def point_purchase_allowed(self, amount, key):
        return amount <= self.unspent_karma

    def undo(self, undo_type):
        """Undoes an adjustment of a given type and updates karma bar."""
        self.adjustments.undo_latest(undo_type)
        self.update_total()

    @property
    def unspent_karma(self):
        return self.good_karma.get() - self.spent_karma

    @property
    def spent_karma(self):
        return self.adjustments.get() + self.applied_karma.get()

    def on_set_otaku(self):
        pass

    def on_unset_otaku(self):
        pass

    def get_otaku_complex_forms_resources(self):
        pass
