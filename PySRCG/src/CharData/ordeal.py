from src.CharData.reportable import Reportable


class Ordeal(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("name", "page")

        self.fill_necessary_fields(necessary_fields, kwargs)
        self.fill_miscellaneous_fields(kwargs)

    def serialize(self):
        return self.properties.copy()
