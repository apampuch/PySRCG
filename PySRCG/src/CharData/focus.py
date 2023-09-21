from src.CharData.reportable import Reportable


class Focus(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("name", "cost", "street_index", "force", "karma_cost", "availability_rating",
                            "availability_time", "availability_unit", "legality", "page")

        # add the bound variable
        if "bound" not in kwargs:
            kwargs["bound"] = False

        # add the necessary fields
        self.fill_necessary_fields(necessary_fields, kwargs)

        # add the other fields
        self.fill_miscellaneous_fields(kwargs)

    def serialize(self):
        return self.properties.copy()

