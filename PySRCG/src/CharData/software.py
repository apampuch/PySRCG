from src.CharData.reportable import Reportable


class Software(Reportable):
    def __init__(self):
        super().__init__()
        self.software_necessary_fields = ["name", "rating", "size", "multiplier", "page"]

    def size(self):
        if self.properties["rating"] == "rating":
            return "rating * rating * multiplier"
        else:
            return self.properties["rating"] * self.properties["rating"] * self.properties["multiplier"]

    def serialize(self):
        # make a copy of properties and remove size from it
        # we do this because the json library can't serialize a function
        ret = self.properties.copy()
        del ret["size"]

        return ret
