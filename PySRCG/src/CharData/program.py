from src.CharData.software import Software


class Program(Software):  # might end up having to extend something like StorableInMemory
    def __init__(self, **kwargs):
        super().__init__()

        # get parent necessary fields
        necessary_fields = ["cost", "street_index", "availability_rating", "availability_time", "availability_unit"]
        necessary_fields += self.software_necessary_fields
        necessary_fields = tuple(necessary_fields)

        # if "options" not in kwargs:
        #     kwargs["options"] = {}  # should be a list of a TBD object, this is NYI

        kwargs["cost"] = self.cost
        kwargs["street_index"] = self.street_index
        kwargs["availability_rating"] = self.availability_rating
        kwargs["availability_time"] = self.availability_time
        kwargs["availability_unit"] = "days"
        kwargs["size"] = self.size

        # validate rating
        if kwargs["rating"] != "rating" and kwargs["rating"] < 1:
            raise ValueError("Rating must be at least 1")
        
        self.fill_necessary_fields(necessary_fields, kwargs)
        self.fill_miscellaneous_fields(kwargs)
        # self.properties["options"] = kwargs["options"]

    def availability_rating(self):
        if self.properties["rating"] == "rating":
            return "CHART NYI"
        elif self.properties["rating"] < 4:
            return 2
        elif 4 <= self.properties["rating"] < 7:
            return 4
        elif 7 <= self.properties["rating"] < 10:
            return 8
        else:
            return 16

    def availability_time(self):
        if self.properties["rating"] == "rating":
            return "CHART NYI"
        elif self.properties["rating"] < 4:
            return 7
        elif 4 <= self.properties["rating"] < 7:
            return 7
        elif 7 <= self.properties["rating"] < 10:
            return 14
        else:
            return 30

    def cost(self):
        if self.properties["rating"] == "rating":
            return "CHART NYI"
        elif self.properties["rating"] < 4:
            return 100 * self.size()
        elif 4 <= self.properties["rating"] < 7:
            return 200 * self.size()
        elif 7 <= self.properties["rating"] < 10:
            return 500 * self.size()
        else:
            return 1000 * self.size()

    def street_index(self):
        if self.properties["rating"] == "rating":
            return "CHART NYI"
        elif self.properties["rating"] < 4:
            return 1
        elif 4 <= self.properties["rating"] < 7:
            return 1.5
        elif 7 <= self.properties["rating"] < 10:
            return 2
        else:
            return 3


# a test of adding properties to the
if __name__ == "__main__":
    test_program = Program(name="TestProg", rating=3, multiplier=2, page=0)

    print(test_program.report())
