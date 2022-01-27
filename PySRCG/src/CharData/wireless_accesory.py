from src.CharData.reportable import Reportable


class WirelessAccessory(Reportable):
    def __init__(self, **kwargs):
        super().__init__()

        necessary_fields = ("name", "cost", "availability_rating", "availability_time", "availability_unit",
                            "street_index", "legality", "page")

        # add the necessary fields
        self.fill_necessary_fields(necessary_fields, kwargs)

        # add the other fields
        self.fill_miscellaneous_fields(kwargs)
        self.properties.update(kwargs)

    def serialize(self):
        return self.properties.copy()
