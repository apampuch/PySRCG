import json
import pathlib
import re

from copy import deepcopy

"""
Don't remove any functions from here for posterity reasons.
"""


def fix_availability(json_object, new_json_object):
    """
    Recursively look for json objects with an availability property that's a string.
    Split that property into three new properties: availability_rating, availability_time, availability_unit
    Remove the old availabiilty property.

    :param json_object: The object to fix.
    :return: A fixed json.
    """

    if type(json_object) is dict:
        for child_key in json_object.keys():
            try:
                child_value = json_object[child_key]  # get the value from the key
                new_child_value = new_json_object[child_key]

                # if the key is called "availability" do our magic
                if child_key == "availability":
                    split_availability(new_json_object)

                # recurse through if it's a dict
                elif type(child_value) is dict:
                    result = fix_availability(child_value, new_child_value)
                    new_json_object[child_key] = result
            # this was used to debug a stupid error I made in the previous line where child_value was actually child_key
            except TypeError:
                # print("OBJECT: " + str(json_object) + " TYPE: " + str(type(json_object)))
                print("KEY: " + str(child_key) + " TYPE: " + str(type(child_key)))
                raise

    return new_json_object


def split_availability(new_json_object):
    old_availability = new_json_object["availability"]
    del new_json_object["availability"]
    if old_availability == "NA" or old_availability == "always":
        new_json_object["availability_rating"] = 0
        new_json_object["availability_time"] = 0
        new_json_object["availability_unit"] = "always"
    else:
        split = re.split(r' |/', old_availability)  # split the availabilty into three parts

        try:
            new_json_object["availability_time"] = split[1]

            # set as int if we can, otherwise keep as string
            try:
                new_json_object["availability_rating"] = int(split[0])
            except ValueError:
                new_json_object["availability_rating"] = split[0]

            try:
                new_json_object["availability_time"] = int(split[1])
            except ValueError:
                new_json_object["availability_time"] = split[1]

            # availability unit is always a string
            new_json_object["availability_unit"] = split[2]

        except IndexError:
            print(old_availability)
            raise

    return new_json_object


if __name__ == "__main__":
    file_path = pathlib.Path.cwd().parent / "src" / "Assets" / "SR3_Core.json"
    new_file_path = pathlib.Path.cwd().parent / "src" / "Assets" / "New_SR3_Core.json"

    with open(file_path) as json_file:
        json_obj = json.loads(json_file.read())
        new_json_obj = deepcopy(json_obj)  # make a deep copy of the json since this makes everything easier
        new_json_obj = fix_availability(json_obj, new_json_obj)
        with open(new_file_path, "w") as new_json_file:
            new_json_file.write(json.dumps(new_json_obj, indent=2))
