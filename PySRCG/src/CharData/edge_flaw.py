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

    def __eq__(self, other):
        if self.properties["name"] == other.properties["name"]:
            if "options" not in self.properties["name"] or "options" not in other.properties["name"]:
                return True
            else:
                # options keys should be same in both, ideally, but return false if they're not
                if list(self.properties["options"].keys()) != list(other.properties["options"].keys()):
                    return False

                for option in self.properties["options"]:
                    if self.properties["options"][option] != other.properties["options"][option]:
                        return False

                return True

    # hash on name and options property
    def __hash__(self):
        hash_master_string = self.properties["name"]

        # sort all the values of the options and slap them into a string
        if "options" in self.properties:
            for option in sorted(list(self.properties["options"].values())):
                hash_master_string += str(option)

        # hash that string
        return hash(hash_master_string)
