from abc import ABC

from src.Tabs.notebook_tab import NotebookTab
from tkinter import *
from tkinter import ttk


class PersonalInfoTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)

        # name box
        ttk.Label(self, text="Name").grid(column=0, row=0)
        self.name_box = Entry(self, width=20)

        # sex box
        ttk.Label(self, text="Sex").grid(column=0, row=1)
        self.male_button = Radiobutton(self, text="M", value="Male")
        self.female_button = Radiobutton(self, text="F", value="Female")
        self.male_button.select()  # select male as default so we have one

        self.name_box.grid(column=1, row=0, columnspan=2)
        self.male_button.grid(column=1, row=1)
        self.female_button.grid(column=2, row=1)

    def on_switch(self):
        pass

    def load_character(self):
        self.name_box.config(textvariable=self.character.name)
        self.male_button.config(variable=self.character.sex)
        self.female_button.config(variable=self.character.sex)

        if self.character.sex.get() == "Male":
            self.male_button.select()
        elif self.character.sex.get() == "Female":
            self.female_button.select()
        else:
            raise ValueError("Gender {} not found.".format(self.character.sex.get()))
