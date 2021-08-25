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
        self.properties["vehicle_accessories"] = []

        if "vehicle_accessories" in kwargs:
            # TODO add reporting for these
            for accessory in kwargs["vehicle_accessories"]:
                try:
                    self.properties["vehicle_accessories"].append(VehicleAccessory(**accessory))
                except TypeError as e:
                    print("Error with {}:".format(kwargs["vehicle_accessories"].name))
                    print(e)
                    print()

            del kwargs["vehicle_accessories"]

        # optional parts, like takeoff/seating
        self.fill_miscellaneous_fields(kwargs)

    def serialize(self):
        ret_dict = self.properties.copy()
        ret_dict["vehicle_accessories"] = []
        for obj in self.properties["vehicle_accessories"]:
            ret_dict["vehicle_accessories"].append(obj.serialize())
        return ret_dict
