from src.CharData.reportable import Reportable
from src.CharData.wireless_accesory import WirelessAccessory


class VehicleAccessory(Reportable):
    def __init__(self, **kwargs):
        super().__init__()

        necessary_fields = ("name", "cost", "availability_rating", "availability_time", "availability_unit",
                            "street_index", "legality", "page")

        # add the necessary fields
        self.fill_necessary_fields(necessary_fields, kwargs)

        if "wireless_accessories" in kwargs:
            self.properties["wireless_accessories"] = []
            # TODO add reporting for these
            for accessory in kwargs["wireless_accessories"]:
                try:
                    self.properties["wireless_accessories"].append(WirelessAccessory(**accessory))
                except TypeError as e:
                    print("Error with {}:".format(kwargs["wireless_accessories"].name))
                    print(e)
                    print()

            del kwargs["wireless_accessories"]

        # add the other fields
        self.properties.update(kwargs)

    def serialize(self):
        ret_dict = self.properties.copy()

        if "wireless_accessories" in self.properties:
            ret_dict["wireless_accessories"] = []
            for obj in self.properties["wireless_accessories"]:
                ret_dict["wireless_accessories"].append(obj.serialize())

        return ret_dict
