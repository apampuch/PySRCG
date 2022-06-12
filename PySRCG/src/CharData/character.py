from src.CharData.statblock import *
from src.CharData.race import *
from tkinter import StringVar


class Character(object):
    def __init__(self, statblock: Statblock = None, file_path: str = ""):
        if statblock is None:
            statblock = Statblock(Human)

        self.statblock = statblock
        self.file_path = file_path

        self.name = StringVar()
        self.sex = StringVar()

        # tabs[0] is personal info tab
        # setup name entry to work with this variable
        app_data.background_tab.tabs[0].name_box.config(textvariable=self.name)
        app_data.background_tab.tabs[0].male_button.config(variable=self.sex)
        app_data.background_tab.tabs[0].female_button.config(variable=self.sex)

    def serialize(self):
        return {
            "statblock": self.statblock.serialize(),
            "name": self.name.get(),
            "sex": self.sex.get()
        }
