from src.CharData.statblock import *
from src.CharData.race import *
from tkinter import StringVar


class Character(object):
    def __init__(self, statblock: Statblock = None, file_path: str = ""):
        if statblock is None:
            statblock = Statblock(Human)

        # variables
        self.statblock = statblock
        self.file_path = file_path

        self.name = StringVar()
        self.real_name = StringVar()
        self.street_names = StringVar()

        self.sex = StringVar()
        self.height = StringVar()
        self.weight = StringVar()
        self.hair = StringVar()
        self.eyes = StringVar()
        self.appearance = StringVar()
        self.archetype = StringVar()

        self.birthdate = StringVar()
        self.birthplace = StringVar()
        self.birth_notes = StringVar()

        self.notes = StringVar()
        self.creator = StringVar()

        # tabs[0] is personal info tab
        # setup name entry to work with this variable
        app_data.background_tab.tabs[0].name_box.config(textvariable=self.name)
        app_data.background_tab.tabs[0].male_button.config(variable=self.sex)
        app_data.background_tab.tabs[0].female_button.config(variable=self.sex)

    def serialize(self):
        return {
            "statblock": self.statblock.serialize(),
            "name": self.name.get(),
            "real_name": self.real_name.get(),
            "sex": self.sex.get(),
            "street_names": self.street_names.get(),
            "height": self.height.get(),
            "weight": self.height.get(),
            "hair": self.hair.get(),
            "eyes": self.eyes.get(),
            "appearance": self.appearance.get(),
            "archetype": self.archetype.get(),
            "birthdate": self.birthdate.get(),
            "birthplace": self.birthplace.get(),
            "birth_notes": self.birth_notes.get(),
            "notes": self.notes.get(),
            "creator": self.creator.get()
        }
