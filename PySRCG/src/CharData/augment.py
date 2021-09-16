"""
This will contain Bioware too eventually.

Bonus attributes an augment can have
holds: This means it's a thing like a cyberear or cybereye that can hold a certain number of mods of a certain type.
          This is an object with a string (type) and a number (essence) representing the type of mod and essence total.
fits: This means it can be held by something like a cybereye or cyberear.
"""
from src.CharData.reportable import Reportable


class Cyberware(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("name", "essence", "cost", "availability_rating", "availability_time", "availability_unit",
                            "street_index", "legality", "page")

        # fields that should be added but not reported like holds/fits
        do_not_report = ["holds", "fits", "mods"]

        # add the necessary fields
        self.fill_necessary_fields(necessary_fields, kwargs)

        # add the other fields
        self.fill_miscellaneous_fields(kwargs, do_not_report)

    def serialize(self):
        return self.properties.copy()
