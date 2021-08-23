from copy import copy
from src.CharData.program import Program
from src.CharData.reportable import Reportable


class Deck(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("name", "cost", "street_index", "availability_rating", "availability_time",
                            "availability_unit", "mpcp", "hardening", "active_memory", "storage_memory", "io_speed",
                            "response_increase", "page")

        self.fill_necessary_fields(necessary_fields, kwargs)

        # also do a special check for stored memory
        if "stored_memory" not in kwargs:
            kwargs["stored_memory"] = []

        try:
            self.properties["stored_memory"] = []
            for stored_software in kwargs["stored_memory"]:
                self.properties["stored_memory"].append(Program(**stored_software))
        except TypeError:
            # on a typeerror do nothing since the save is formatted wrong
            print("Save formatted wrong, use a list of Programs")
            raise

        # also handle the persona
        if "persona" not in kwargs:
            self.properties["persona"] = {
                "bod": 1,
                "evasion": 1,
                "masking": 1,
                "sensor": 1
            }
        else:
            self.properties["persona"] = kwargs["persona"]

    def total_persona_points(self) -> int:
        return self.properties["mpcp"] * 3

    def serialize(self):
        # fix the _dict so that the store memory programs are also dicts
        ret_dict = self.properties.copy()
        ret_dict["stored_memory"] = []
        for obj in self.properties["stored_memory"]:
            ret_dict["stored_memory"].append(obj.serialize())
        return ret_dict
