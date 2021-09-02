from src.calculable_ordered_dict import CalculableOrderedDict


def report_dict(field_name, field_value):
    # if it's "options" just skip it
    if field_name == "options":
        return ""

    # format field_name
    field_name = field_name.replace("_", " ")
    field_name = field_name.capitalize()

    if type(field_value) is dict:
        # get sub _dict since that's the one we want
        # there should only be one
        sub_dict = list(field_value.values())[0]
        # construct the string
        to_add = "{}:\n".format(field_name)
        for k in sub_dict.keys():
            v = sub_dict[k]

            # replace semicolons in k
            if k[0] == ";":
                k = k.replace(";", "<=")
            elif k[-1] == ";":
                k = k.replace(";", "+")
            else:
                k = k.replace(";", "-")

            to_add += "  {}\t:  {}\n".format(k, v)
    else:
        to_add = "{}: {}\n".format(field_name, field_value)

    return to_add


class Reportable:
    # Find a way to have it so that some miscellaneous fields aren't reported. We may not run into that but
    # we probably will at some point.
    def __init__(self):
        self.properties = CalculableOrderedDict()
        self.reported_fields = []

    def fill_necessary_fields(self, necessary_fields, _dict, report=True):
        """
        Fills the necessary fields. Throws an error if _dict doesn't contain the fields we want.
        :param necessary_fields: Tuple of all of the necessary fields.
        :param report: If true, the field will be reported with report()
        :param _dict:
        """
        keys = _dict.keys()
        for field in necessary_fields:
            if field not in keys:
                raise ValueError(f"{self.properties['name']} needs to have {field}!")
            else:
                self.properties[field] = _dict[field]
                del _dict[field]
                if report:
                    self.reported_fields.append(field)

    def add_field(self, field, value, report=True):
        self.properties[field] = value
        if report:
            self.reported_fields.append(field)

    def fill_miscellaneous_fields(self, _dict, do_not_report=()):
        """
        Fills in non-necessary fields.
        :param _dict: Dict of things to add.
        :param do_not_report: Tuple of fields that should not appear in the report.
        """
        for key in _dict:
            self.properties[key] = _dict[key]
            if key not in do_not_report:
                self.reported_fields.append(key)

    def report(self):
        report_str = "{}\n\n".format(self.properties["name"])

        for field in self.reported_fields:
            if field == "availability_rating":
                report_str += self.report_availability()
            elif field == "availability_time" or field == "availability_unit":
                continue
            else:
                report_str += report_dict(field, self.properties[field])

        return report_str

    def report_availability(self) -> str:
        """
        This reports the availability in a rating/time unit format. e.g. 6/4 days
        NOT ALL REPORTABLES MAY USE THIS.
        :return: String representing availability.
        """
        try:
            # if the availability_unit is a string then just print that string
            if type(self.properties["availability_rating"]) == str:
                return f"Availability: {self.properties['availability_rating']}\n"
            elif self.properties["availability_rating"] == 0:
                return "Availability: Always\n"
            else:
                return "Availability: {}/{} {}\n".format(self.properties["availability_rating"],
                                                         self.properties["availability_time"],
                                                         self.properties["availability_unit"])
        # return blank string if these fields don't exist
        except KeyError:
            return ""

    @property
    def name(self):
        return self.properties["name"]

    @name.setter
    def name(self, value):
        self.properties["name"] = value
