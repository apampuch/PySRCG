from abc import ABC
from tkinter import IntVar

from src import app_data
from src.GenModes.gen_mode import GenMode
from src.adjustment import AdjustmentsContainer, Adjustment


class Finalized(GenMode, ABC):
    """
    The "genmode" used for after a character is finalized.
    Assume that a character's karma is unspent until spent.
    """

    adjustments: AdjustmentsContainer

    def __init__(self, data=None, metatype=None):
        super().__init__()

        self.starting_skills_max = 99   # why you'd ever need more than 100 dice idk
        self.good_karma = IntVar()      # don't set directly, use self.set_total_karma
        self.karma_pool = IntVar()      # never set directly, only use set_total_karma
        self.applied_karma = IntVar()   # applied karma is the amount of karma spent from applied changes
        self.karma_pool.set(1)          # yes we're setting it here, don't get smart with me

        if data is not None and metatype is not None:
            self.set_total_karma(data["total_karma"], metatype)
            self.applied_karma.set(data["applied_karma"])

        self.adjustments = AdjustmentsContainer()

        self.karma_bar_vals = {
            "attributes": (self.adjustments, self.good_karma),
            "spells": (self.adjustments, self.good_karma),
            "skills": (self.adjustments, self.good_karma),
        }

    def total_karma(self):
        """
        Returns total karma, good karma plus karma pool.
        The -1 is to offset the one free karma pool.
        :return: Good karma + karma pool.
        """
        return self.karma_pool.get() + self.good_karma.get() - 1

    def add_karma(self, amount, metatype):
        """
        Adds karma to the total.
        :param amount: Amount of good karma to add.
        :param metatype: Metatype of the character. This matters due to humans getting more Karma Pool.
        """
        total = self.total_karma() + amount
        self.set_total_karma(total, metatype)

    def sub_karma(self, amount, metatype):
        """
        Subtracts karma to the total. Won't go below 0.
        :param amount: Amount of good karma to subtract.
        :param metatype: Metatype of the character. This matters due to humans getting more Karma Pool.
        """
        total = max(self.total_karma() - amount, self.spent_karma)  # so we don't go below 0
        self.set_total_karma(total, metatype)

    # calculates good karma and subtracts the karma pool tax
    def set_total_karma(self, total, metatype):
        self.karma_pool.set(total // metatype.karma_div + 1)         # +1 because you start with 1 karma pool
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

    def update_total(self, amount=None, key=None):  # set defaults here so we can call without args
        # Literally ignore everything and just refresh the karma bar.
        app_data.top_bar.update_karma_label(self.spent_karma,
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
        raise Exception("This should never be called when finalized.")

    def on_unset_otaku(self):
        raise Exception("This should never be called when finalized.")

    def get_otaku_complex_forms_resources(self):
        """Should this ever even get called? Do we need this when Finalized?"""
        pass
