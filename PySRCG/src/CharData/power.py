from src.CharData.reportable import Reportable


class Power(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("name", "cost", "max_levels", "page", "level")

        # always have default level 1
        if "level" not in kwargs:
            kwargs["level"] = 1

        self.fill_necessary_fields(necessary_fields, kwargs)
        self.fill_miscellaneous_fields(kwargs)

    def serialize(self):
        return self.properties.copy()
