from copy import copy
from src.CharData.program import Program


class Deck:
    def __init__(self, name, mpcp, availability_rating, availability_time, availability_unit, hardening, active_memory,
                 storage_memory, io_speed, response_increase, cost, street_index, page, stored_memory=None, persona=None):

        self.name = name
        self.availability_rating = availability_rating
        self.availability_time = availability_time
        self.availability_unit = availability_unit
        self.mpcp = mpcp
        self.hardening = hardening
        self.active_memory = active_memory
        self.storage_memory = storage_memory
        self.io_speed = io_speed
        self.response_increase = response_increase
        self.cost = cost
        self.street_index = street_index
        self.page = page
        self.stored_memory = []  # stored programs n shit

        if stored_memory is not None:
            try:
                for stored_software in stored_memory:
                    self.stored_memory.append(Program(**stored_software))
            except TypeError:
                # on a typeerror do nothing since the save is formatted wrong
                print("Save formatted wrong, use a list of Programs")
                raise

        # self.stored_memory = stored_memory

        if persona is None:
            self.persona = {
                "bod": 1,
                "evasion": 1,
                "masking": 1,
                "sensor": 1
            }
        else:
            self.persona = persona

    def report(self) -> str:
        return "{}\n\n" \
               "Availability: {}/{} {}\n" \
               "MPCP: {}\n" \
               "Hardening: {}\n" \
               "Active Memory: {}\n" \
               "Storage Memory: {}\n" \
               "I/O Speed: {}\n" \
               "Response Increase: {}\n" \
               "Cost: {}\n" \
               "Street Index: {}\n" \
            .format(self.name,
                    self.availability_rating,
                    self.availability_time,
                    self.availability_unit,
                    self.mpcp,
                    self.hardening,
                    self.active_memory,
                    self.storage_memory,
                    self.io_speed,
                    self.response_increase,
                    self.cost,
                    self.street_index)

    def total_persona_points(self) -> int:
        return self.mpcp * 3

    def serialize(self):
        # fix the dict so that the store memory programs are also dicts
        ret_dict = copy(self.__dict__)
        ret_dict["stored_memory"] = []
        for obj in self.stored_memory:
            ret_dict["stored_memory"].append(obj.__dict__)
        return ret_dict
