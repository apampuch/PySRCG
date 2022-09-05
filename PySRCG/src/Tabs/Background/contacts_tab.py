from abc import ABC
from tkinter import *
from tkinter import ttk

from src.Tabs.notebook_tab import NotebookTab


class ContactsTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)

        self.list_frame = Frame(self)
        self.contacts_listbox = Listbox(self)
        self.add_button = Button(self)
        self.remove_button = Button(self)

        self.contact_frame = Frame(self)

        self.name_label = Label(self)
        self.name_entry = Entry(self)

        self.archetype_label = Label(self)
        self.archetype_entry = Entry(self)

        self.location_label = Label(self)
        self.location_entry = Entry(self)

        self.LTG_label = Label(self)
        self.LTG_entry = Entry(self)

        self.affiliation_label = Label(self)
        self.affiliation_combobox = ttk.Combobox(self)

        self.description_label = Label(self)
        self.description_text = Text(self)

        self.history_label = Label(self)
        self.history_text = Text(self)

        # grids

    def on_listbox_click(self):
        pass

    def on_add_click(self):
        pass

    def on_remove_click(self):
        pass

    def reload_data(self):
        pass

    def on_switch(self):
        pass

    def load_character(self):
        pass

