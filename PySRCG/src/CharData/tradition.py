"""
it has been settled that we'll only use one tradition class
json needs a list of allowed aspects
json needs a list of foci and descriptions for each
"""
from tkinter import *
from tkinter import ttk


class Tradition:
    def __init__(self, name, allowed_aspects, allowed_foci, focus_name, page, book, always_has_focus=False):
        self.name = name
        self.allowed_aspects = allowed_aspects
        self.allowed_foci = allowed_foci
        self.always_has_focus = always_has_focus
        self.focus_name = focus_name
        self.page = page
        self.book = book

    def serialize(self):
        return self.__dict__
