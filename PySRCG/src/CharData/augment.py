"""
This will contain Bioware too eventually.

Bonus attributes an augment can have
holds: This means it's a thing like a cyberear or cybereye that can hold a certain number of mods of a certain type.
          This is an object with a string (type) and a number (essence) representing the type of mod and essence total.
fits: This means it can be held by something like a cybereye or cyberear.
"""
from src.statblock_modifier import StatMod


class Cyberware:
    def __init__(self, name, essence, cost, availability_rating, availability_time, availability_unit, street_index,
                 legality, page, holds=None, fits=None, grade="standard", rating=None, mods=None, **kwargs):
        if mods is None:
            mods = {}
        self.name = name
        self.essence = essence
        self.cost = cost
        self.availability_rating = availability_rating
        self.availability_time = availability_time
        self.availability_unit = availability_unit
        self.street_index = street_index
        self.legality = legality
        self.holds = holds
        self.fits = fits
        self.page = page
        self.grade = grade  # standard == None
        self.mods = mods
        self.rating = rating
        if "other_fields" in kwargs.keys():
            self.other_fields = kwargs["other_fields"]
        else:
            self.other_fields = kwargs

    def serialize(self):
        return self.__dict__

    def report(self):
        info = "{}\n\n" \
               "Essence Cost: {}\n" \
               "Price: {}\n" \
               "Availability: {}/{} {}\n" \
               "Street Index: {}\n" \
               "Legality: {}\n" \
               "Mods: {}\n" \
                   .format(self.name,
                           self.essence,
                           self.cost,
                           self.availability_rating, self.availability_time, self.availability_unit,
                           self.street_index,
                           self.legality,
                           self.mods) + \
               ("Rating: {}\n".format(self.rating) if self.rating is not None else "")

        for key in self.other_fields.keys():
            info += "{}: {}\n".format(key.replace("_", " ").capitalize(), self.other_fields[key])

        info += "Page: {}".format(self.page)

        return info
