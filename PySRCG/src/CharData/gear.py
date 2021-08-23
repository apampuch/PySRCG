from src.CharData.reportable import Reportable


class Gear(Reportable):
    def __init__(self, **kwargs):
        super().__init__()
        necessary_fields = ("name", "weight", "cost", "street_index", "availability_rating", "availability_time",
                            "availability_unit", "legality", "page")

        # add the necessary fields
        self.fill_necessary_fields(necessary_fields, kwargs)

        # add the other fields
        self.fill_miscellaneous_fields(kwargs)

    def serialize(self):
        return self.properties.copy()


def find_gear_by_dict_load(_dict):
    """
    This function is used for loading saves. Saved items have their name on the same
    tree level as the rest of the game.
    """
    return find_gear_by_dict(_dict)


def find_gear_by_dict(_dict):
    """This function isn't REALLY necessary I'm just too lazy to replace it"""
    return Gear(**_dict)


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
