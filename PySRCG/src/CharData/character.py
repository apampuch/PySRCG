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

    def serialize(self):
        return {
            "statblock": self.statblock.serialize(),
            "name": self.name.get(),
            "sex": self.sex.get()
        }
