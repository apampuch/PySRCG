from src.CharData.reportable import Reportable


class Echo(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("name", "no_duplicates", "page")
        self.fill_necessary_fields(necessary_fields, kwargs)

    def serialize(self):
        return self.properties
