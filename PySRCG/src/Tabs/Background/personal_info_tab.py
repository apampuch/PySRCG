from src.Tabs.notebook_tab import NotebookTab
from tkinter import *
from tkinter import ttk


class PersonalInfoTab(NotebookTab):
    def __init__(self, parent):
        super().__init__(parent)

        # name box
        ttk.Label(self, text="Name").grid(column=0, row=0)
        self.name_box = Entry(self, width=20, textvariable=self.character.name)

        # sex box
        ttk.Label(self, text="Sex").grid(column=0, row=1)
        self.male_button = Radiobutton(self, text="M", variable=self.character.sex, value="Male")
        self.female_button = Radiobutton(self, text="F", variable=self.character.sex, value="Female")
        self.male_button.select()  # select male as default so we have one

        self.name_box.grid(column=1, row=0, columnspan=2)
        self.male_button.grid(column=1, row=1)
        self.female_button.grid(column=2, row=1)

    def on_switch(self):
        pass

    def load_character(self):
        self.name_box.config(textvariable=self.character.name)
        if self.character.sex.get() == "Male":
            self.male_button.select()
        elif self.character.sex.get() == "Female":
            self.female_button.select()
        else:
            raise ValueError("Gender {} not found.".format(self.character.sex.get()))
