from src.CharData.reportable import Reportable


class EdgeFlaw(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("cost",)
        do_not_report = ["mods",]

        self.fill_necessary_fields(necessary_fields, kwargs)
        self.fill_miscellaneous_fields(kwargs, do_not_report)

    def serialize(self):
        return self.properties.copy()
