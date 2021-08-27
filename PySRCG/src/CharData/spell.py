from src.CharData.reportable import Reportable


class Spell(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("name", "type", "target", "duration", "drain", "force", "page")
        
        self.fill_necessary_fields(necessary_fields, kwargs)
        self.fill_miscellaneous_fields(kwargs)

    def force_and_name(self):
        return "[{}] {}".format(self.properties["force"], self.properties["name"])

    def serialize(self):
        return self.properties.copy()
