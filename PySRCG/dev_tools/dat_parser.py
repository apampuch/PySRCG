import json
from collections import OrderedDict
from typing import List


# copy and paste this for reference
sr3_books = ("cc", "mits", "mm", "mat", "r3", "sr3", "src", "ssg", "sota", "sota2", "tal", "twl", "yotc", "sea")


def split_tab_and_name(item: str) -> List[str]:
    # splits first whitespaces on left and right
    # used to separate "scope" from name and whatever that other number is
    a = item.split(maxsplit=1)
    b = a[1].rsplit(maxsplit=1)
    del a[1]
    return a + b


def extract_name(item: List[str]) -> List[str]:
    # just extracts the name from the nsrcg tab-name-type formatting
    a = item[0].split(maxsplit=1)  # split left
    b = a[1].rsplit(maxsplit=1)  # split right
    del a[1]
    return [b[0]] + item[1:]


def extract_book_page(item: List[str]) -> List[str]:
    page_book = item[1].split(".")
    return item[:1] + page_book + item[2:]


def remove_rating(name: str) -> bool:
    """Returns false if no rating present. Returns true and strips if present."""
    ratings = {"[1]": 1, "[2]": 2, "[3]": 3, "[4]": 4, "[5]": 5, "[6]": 6, "[7]": 7, "[8]": 8, "[9]": 9, "[10]": 10}

    for r in ratings:
        if r in name:
            name.replace(r, "")
            return ratings[r]

    return False


def parse_text(filename, allowed_books):
    """
    Turns text into some kind of usable data.
    """
    json_dict = OrderedDict()

    with open(filename, "r") as datfile:
        # formats, a list of lists, first is blank so we can line up things directly
        formats: List[List]
        formats = [[]]

        for line in datfile.readlines():
            # ignore commented lines
            if line[0] == "!":
                continue

            # if it's just a divider, skip it for now
            if "|" not in line:
                continue

            # split bars
            components: List
            components = line.split("|")

            # if it starts with a 0, it's a format and throw it into the formats list
            if components[0][0] == "0":
                # these are worthless to us
                del components[2]
                del components[0]
                components = extract_book_page(components)
                del components[1]
                components[-1] = components[-1].rstrip("\n")
                components = list(map(lambda x: x.lower(), components))
                formats.append(components)
                # append a container to the json dict
                if components[0] not in json_dict.keys():
                    json_dict[components[0]] = OrderedDict()
            # otherwise it's not and we need to do other things
            else:
                # find what format to use
                try:
                    index = int(components[0].rsplit(maxsplit=1)[1])
                except ValueError:
                    print(f"Invalid index {index}")
                    continue

                # format stuff
                components = extract_name(components)
                components = extract_book_page(components)
                components[-1] = components[-1].rstrip("\n")

                # skip if it's not a book we can use
                try:
                    if components[1] not in allowed_books:
                        continue
                except IndexError:
                    print(f"ERROR: {components[1]}")

                # delete book name now that we don't need it
                del components[1]

                # if we have the wrong length of type we need to just keep going
                current_format = formats[index]
                if len(components) != len(current_format):
                    continue

                # make the dict
                dict_obj = OrderedDict()

                for i in range(1, len(components)-1):  # make it len - 1 if you want to skip notes
                    dict_obj[current_format[i]] = components[i]

                # find the correct subdict and set name
                json_dict[current_format[0]][components[0]] = dict_obj

        return json_dict


# def fix_cyberware(cyber_dict):
#     new_dict = {}  # a duplicate dict to build so we can loop
#
#     for name in cyber_dict["cyberware"].keys():
#         obj = cyber_dict["cyberware"][name]
#
#         # check to see if we have a rating
#         rating = remove_rating(name)
#         if rating:
#             # if we find it has a rating, check the dict to see if we already that in it
#             for category in new_dict:
#                 # if it's there, append to the list
#                 if name in new_dict[category]:
#                     completed_obj = new_dict[category][name]
#                     for k in completed_obj:
#                         completed_obj[k].append(obj[k])
#             # otherwise fix it up and add it to the dict
#             # make everything a list
#             for k in obj:
#                 obj[k] = [obj[k]]
#
#             category =
#
#             new_dict[category][name] = obj
#
#     return new_dict


def fix_spells(spells_dict):
    class_correction_dict = {
        "C": "Combat",
        "D": "Detection",
        "H": "Health",
        "I": "Directed Illusion",
        "N": "Indirect Illusion",
        "M": "Control Manipulation",
        "E": "Elemental Manipulation",
        "T": "Telekinetic Manipulation",
        "Z": "Transformation Manipulation"
    }
    duration_correction_dict = {
        "I": "Instant",
        "S": "Sustained",
        "P": "Permanent"
    }
    range_correction_dict = {
        "T": "Touch",
        "T(V)": "Touch",
        "LOS": "Line of Sight",
        "LOS(A)": "Line of Sight (Area Effect)",
        "LOS/D": "Line of Sight (Directional)",
        "T/D": "Touch (Directional)",
        "T/A": "Touch (Area)",
        "P": "Personal",
        "L": "Line of Sight"
    }
    type_correction_dict = {
        "M": "Mana",
        "P": "Physical"
    }
    target_correction_list = {
        "W": "Willpower",
        "I": "Intelligence",
        "C": "Charisma",
        "B": "Body",
        "Q": "Quickness",
        "S": "Strength",
        "REA": "Reaction",
        "F": "Force",
        "OR": "Object Resistance",
        "DT": "Detection Table",
        "TOX": "Toxin Strength",
        "Att": "Attribute",
        "10-E": "10 - Essence",
        "DP": "Disease Power",
        "4+MIN V": "4 + Minutes",
        "*": "Length in CM / 3",
        "Pfire": "Power rating of fire"
    }

    for key in spells_dict["spells"].keys():
        spells_dict["spells"][key].move_to_end("page")
        spells_dict["spells"][key]["page"] = int(spells_dict["spells"][key]["page"])
        spells_dict["spells"][key]["class"] = class_correction_dict[spells_dict["spells"][key]["class"]]
        spells_dict["spells"][key]["duration"] = duration_correction_dict[spells_dict["spells"][key]["duration"]]
        if spells_dict["spells"][key]["range"] in range_correction_dict:
            spells_dict["spells"][key]["range"] = range_correction_dict[spells_dict["spells"][key]["range"]]
        else:
            print(f"{key}: {spells_dict['spells'][key]}")
        spells_dict["spells"][key]["type"] = type_correction_dict[spells_dict["spells"][key]["type"]]

        # do this to easily fix the weird shit in target correction
        target = spells_dict["spells"][key]["target"]

        # strip spell and voluntary and threshold
        stripped = target.replace("(R)", "").replace("(V)", "").replace("(T)", "").replace("(RC)", "")

        # if it's an integer, don't look in the list
        try:
            x = int(stripped)  # just to see if we can cast to int
            corrected = stripped
        except ValueError:
            if stripped in target_correction_list:
                corrected = target_correction_list[stripped]
            else:
                print(target)
                continue

        if "(R)" in target:
            corrected += " (Spell Resistance)"

        if "(V)" in target:
            corrected += " (Voluntary)"

        if "(T)" in target:
            corrected += " (Threshold)"

        if "(RC)" in target:
            corrected += " (Ranged Combat)"

        spells_dict["spells"][key]["target"] = corrected


if __name__ == "__main__":
    json_dict = parse_text("./nsrcg_dats/cyber.dat.dat", ["sr3"])
    fix_spells(json_dict)
    with open("new_spells.json", "w") as new_file:
        json.dump(json_dict, new_file, indent=2)
    # print(json.dumps(json_dict, indent=2))
