def report_dict(field_name, field_value):
    # format field_name
    field_name = field_name.replace("_", " ")
    field_name = field_name.capitalize()

    if type(field_value) is dict:
        # get sub dict since that's the one we want
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


class Gear(object):
    def __init__(self, **kwargs):
        try:
            super().__init__()
            self.name = kwargs["name"]; del kwargs["name"]
            self.weight = kwargs["weight"]; del kwargs["weight"]
            self.availability_rating = kwargs["availability_rating"]; del kwargs["availability_rating"]
            self.availability_time = kwargs["availability_time"]; del kwargs["availability_time"]
            self.availability_unit = kwargs["availability_unit"]; del kwargs["availability_unit"]
            self.cost = kwargs["cost"]; del kwargs["cost"]
            self.street_index = kwargs["street_index"]; del kwargs["street_index"]
            self.legality = kwargs["legality"]; del kwargs["legality"]
            self.page = kwargs["page"]; del kwargs["page"]
            self.other_fields = kwargs
        except KeyError:
            print(self.name)
            raise

    def report(self) -> str:
        info = "{}\n\n".format(self.name)

        info += report_dict("Weight", self.weight)
        info += self.report_availability()
        info += report_dict("Cost", self.cost)
        info += report_dict("Street Index", self.street_index)
        info += report_dict("Legality", self.legality)

        for key in self.other_fields.keys():
            info += report_dict(key, self.other_fields[key])

        info += "Page: {}".format(self.page)

        return info

    def report_availability(self):
        if self.availability_unit == "always":
            return "Availability: Always\n"
        else:
            return "Availability: {}/{} {}\n".format(self.availability_rating, self.availability_time, self.availability_unit)

    def serialize(self):
        # copy the dict, remove other_fields, and merge it directly into the dict
        d = self.__dict__.copy()
        del d["other_fields"]
        d.update(self.other_fields)

        return d


def find_gear_by_dict_load(_dict):
    """
    This function is used for loading saves. Saved items have their name on the same
    tree level as the rest of the game.
    """
    if "name" in _dict.keys():
        name = _dict["name"]
        del _dict["name"]
        return find_gear_by_dict(name, _dict)
    else:
        raise ValueError('_dict needs a "name"')


def find_gear_by_dict(name, _dict):
    """This function isn't REALLY necessary I'm just too lazy to replace it"""
    return Gear(name=name, **_dict)


def make_dict(o):
    return {o.name: o.__dict__}


if __name__ == "__main__":
    import json
    import pathlib

    json_path = pathlib.Path.cwd().parent / "Assets" / "SR3_Core.json"

    with open(json_path, "r") as json_file:
        game_data = json.load(json_file)
        rocket_data = game_data["Items"]["Weapons"]["Ammunition"]["Rockets"]["Anti-Vehicle"]
        rocket_item = Gear(name="Anti-Vehicle", **rocket_data)
        print(rocket_item.report())
        s_rocket = rocket_item.serialize()
        print(s_rocket)
