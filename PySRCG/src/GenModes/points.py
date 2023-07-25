from abc import ABC

from src.GenModes.gen_mode import GenMode


class Points(GenMode, ABC):
    def __init__(self):
        super().__init__()
        self.starting_skills_max = 6

    def get_generated_value(self, key):
        pass

    def update_karma_label(self, tab):
        pass

    def setup_ui_elements(self):
        pass

    def serialize(self):
        pass

    def update_total(self, amount, key):
        pass

    def point_purchase_allowed(self, amount, key):
        """Ignore key since we draw from the same pool."""
        pass

    def on_set_otaku(self):
        pass

    def on_unset_otaku(self):
        pass

    def get_otaku_complex_forms_resources(self):
        pass


