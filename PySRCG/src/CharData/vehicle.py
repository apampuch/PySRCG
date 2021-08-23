from copy import copy

from src.CharData.reportable import Reportable
from src.CharData.vehicle_accessory import VehicleAccessory


class Vehicle(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("name", "cost", "availability_rating", "availability_time", "availability_unit",
                            "street_index", "handling", "speed", "accel", "body", "armor", "sig", "autonav",
                            "pilot", "sensor", "cargo", "load", "page")

        self.fill_necessary_fields(necessary_fields, kwargs)

        # add accessories property no matter what
        self.properties["accessories"] = []

        if "accessories" in kwargs:
            # TODO add reporting for these
            for accessory in kwargs["accessories"]:
                try:
                    self.properties["accessories"].append(VehicleAccessory(**accessory))
                except TypeError as e:
                    print("Error with {}:".format(kwargs["accessories"].name))
                    print(e)
                    print()

            del kwargs["accessories"]

        # optional parts, like takeoff/seating
        self.fill_miscellaneous_fields(kwargs)

    def serialize(self):
        ret_dict = self.properties.copy()
        ret_dict["accessories"] = []
        for obj in self.properties["accessories"]:
            ret_dict["accessories"].append(obj.serialize())
        return ret_dict
