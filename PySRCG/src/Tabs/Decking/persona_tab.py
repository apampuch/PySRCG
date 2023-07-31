from abc import ABC
from typing import Any

from src import app_data
from src.Tabs.notebook_tab import NotebookTab
from tkinter import *
from tkinter import ttk


class PersonaTab(NotebookTab, ABC):
    """
    Select deck via dropdown
    adjust attributes
    list reaction, init, hacking pool
    box with all programs from all sources - XXmp - source
    buttons to add/remove from active memory
    list of selected deck's active memory
    label updated with cur/max mp
    """
    def __init__(self, parent):
        super().__init__(parent, "PersonaTab")

        self.slider_vars = {}
        self.slider_old_vals = {}

        self.sliders = {}
        self.attribute_labels = {}
        self.value_labels = {}

        self.persona_total = IntVar()

        # combobox with all decks
        self.deck_box = ttk.Combobox(self, state="readonly")
        self.deck_box.bind("<<ComboboxSelected>>", self.on_choose_deck)

        self.persona_frame = ttk.LabelFrame(self, text="Persona")

        attributes = ["bod", "evasion", "masking", "sensor"]
        self.current_row = 1
        for attr in attributes:
            self.setup_slider_and_label(attr)

        self.initiative_frame = ttk.LabelFrame(self, text="Initiative & Reaction")

        self.natural_reaction_var = IntVar()
        self.natural_initiative_var = StringVar()
        self.natural_reaction_value = Label(self.initiative_frame, textvariable=self.natural_reaction_var)
        self.natural_initiative_value = Label(self.initiative_frame, textvariable=self.natural_initiative_var)
        self.dni_reaction_var = IntVar()
        self.dni_initiative_var = StringVar()
        self.dni_reaction_value = Label(self.initiative_frame, textvariable=self.dni_reaction_var)
        self.dni_initiative_value = Label(self.initiative_frame, textvariable=self.dni_initiative_var)

        # grids

        self.deck_box.grid(column=1, row=1)
        self.persona_frame.grid(column=1, row=2)
        self.initiative_frame.grid(column=1, row=3)

        Label(self.initiative_frame, text="Reaction (Physical)").grid(column=1, row=1)
        self.natural_reaction_value.grid(column=2, row=1)
        Label(self.initiative_frame, text="Initiative (Physical)").grid(column=1, row=2)
        self.natural_initiative_value.grid(column=2, row=2)
        Label(self.initiative_frame, text="Reaction (DNI)").grid(column=1, row=3)
        self.dni_reaction_value.grid(column=2, row=3)
        Label(self.initiative_frame, text="Initiative (DNI)").grid(column=1, row=4)
        self.dni_initiative_value.grid(column=2, row=4)

    def setup_slider_and_label(self, key):
        """Initial setup. Should only be run once per attribute."""
        self.slider_vars[key] = IntVar()             # this is the internal variable
        self.slider_vars[key].set(1)                 # initialize it to 1
        self.slider_old_vals[key] = IntVar()         # this is to correct for when we try to go over our total
        self.slider_old_vals[key].set(1)             # initialize it to 1

        self.attribute_labels[key] = ttk.Label(self.persona_frame, text=key.capitalize())
        self.value_labels[key] = ttk.Label(self.persona_frame, text="1")
        self.sliders[key] = Scale(self.persona_frame,
                                  from_=1, to=1,
                                  variable=self.slider_vars[key],
                                  command=lambda x: self.on_set_slider_value(key, x),
                                  orient=HORIZONTAL, showvalue=False)

        self.attribute_labels[key].grid(column=1, row=self.current_row)
        self.value_labels[key].grid(column=2, row=self.current_row)
        self.sliders[key].grid(column=3, row=self.current_row)

        self.current_row += 1

    @property
    def current_deck(self) -> Any | None:
        if not self.deck_list:  # if empty, this makes it shut up
            return None
        return self.deck_list[self.deck_box.current()]

    @property
    def deck_list(self):
        decks = []

        for deck in self.statblock.decks:
            decks.append(deck)

        return decks

    @property
    def deck_list_names(self):
        return list(map(lambda x: x.name, self.deck_list))

    def on_set_slider_value(self, key, value):
        value = int(value)

        # test to make sure value is valid
        # add value of all sliders together
        slider_total = 0
        for val in self.sliders.values():
            slider_total += val.get()

        # We do this because the sliders get the attempted set value rather than the value before the set.
        # We just subtract 1, because we can't go below 0 anyway, and we need to check that we're less than
        # or equal to a threshold in point_purchase_allowed
        # If we don't do this, we'll be limited to a maximum of 1 less than our intended maximum.
        slider_total -= 1

        # check if purchase is allowed
        if slider_total >= self.current_deck.total_persona_points():
            value = self.slider_old_vals[key].get()
            self.sliders[key].set(value)
        else:
            self.slider_old_vals[key].set(value)
            self.current_deck.properties["persona"][key] = value

        # set label values
        self.value_labels[key].config(text=self.sliders[key].get())

        self.calculate_total()

    # noinspection PyUnusedLocal
    def on_choose_deck(self, event):
        # make it shut up if we have no decks
        # tab will be invisible if we have no decks anyway
        if self.current_deck is None:
            return

        # setup sliders
        for key in self.sliders.keys():
            # set slider maximums
            self.sliders[key].config(to=self.current_deck.properties["mpcp"])
            self.sliders[key].set(self.current_deck.properties["persona"][key])

            # set other deck stats
            response_increase = self.current_deck.properties["response_increase"]
            natural_reaction = min(self.statblock.calculate_natural_attribute("reaction") + response_increase * 2, 10)
            natural_initiative = \
                f"{min(response_increase + self.statblock.calculate_natural_attribute('initiative'), 5)}d6"
            dni_reaction = min(self.statblock.intelligence + response_increase * 2 + 2, 10)
            dni_initiative = \
                f"{min(response_increase + self.statblock.calculate_natural_attribute('initiative') + 1, 5)}d6"
            self.natural_reaction_var.set(natural_reaction)
            self.natural_initiative_var.set(natural_initiative)
            self.dni_reaction_var.set(dni_reaction)
            self.dni_initiative_var.set(dni_initiative)

        self.update_karma_bar()
        self.calculate_total()

    def update_karma_bar(self):
        progress_bar = app_data.top_bar.karma_bar
        progress_bar.configure(variable=self.persona_total, maximum=self.current_deck.total_persona_points())

    def on_switch(self):
        selected_deck: str | None

        # get current deck before changing
        if self.deck_box.current() == -1:
            selected_deck = None
        else:
            selected_deck = self.deck_box["values"][self.deck_box.current()]

        # populate deck list
        self.deck_box.config(values=self.deck_list_names)

        # if the deck we had selected before doesn't exist, or we didn't have one, select a new one if we have any decks
        if (selected_deck is None or selected_deck not in self.deck_list_names) and len(self.deck_list) > 0:
            self.deck_box.current(0)

        self.on_choose_deck(None)

    def calculate_total(self):
        total = 0

        for key in self.sliders.keys():
            total += self.sliders[key].get()

        self.persona_total.set(total)

        app_data.top_bar.update_karma_label(total, self.current_deck.total_persona_points(), "Persona Tab")

    def load_character(self):
        pass
