from collections import OrderedDict

"""
These are all of the functions that should be used to upgrade a save file from one version to the next.
When a save from an older version is loaded, the current version should be found, then the following functions
called consecutively until the save is upgraded to the latest version.
"""


# TODO test more
def v0_1_to_v0_2(save_file):
    """
    v0.1 -> v0.2 gets rid of the attributes_to_calculate property
    """

    save_file["save_version"] = 0.2

    recurse_delete_attributes_to_calculate(save_file)


def recurse_delete_attributes_to_calculate(dict_):
    """Used by v0_1_to_v0_2"""

    if "attributes_to_calculate" in dict_:
        del dict_["attributes_to_calculate"]

    for child_key in dict_:
        child_val = dict_[child_key]

        if type(child_val) is dict:
            recurse_delete_attributes_to_calculate(child_val)
        elif type(child_val) == list:
            for item in child_val:
                if type(item) is dict:
                    recurse_delete_attributes_to_calculate(item)


"""
Use an ordered _dict to store these. 
"""
upgrade_funcs = OrderedDict()

upgrade_funcs[0.1] = v0_1_to_v0_2


def upgrade_from_version(save_file):
    try:
        version = save_file["save_version"]
        try:
            # find the index of the key we're looking for
            version_keys = list(upgrade_funcs)
            start_index = version_keys.index(version)

            # print all values to the end starting with the key we found
            for key in version_keys[start_index:]:
                upgrade_funcs[key](save_file)
        except ValueError:
            print(f"{version} is not a valid save version.")
            return
    except ValueError:
        print("Save file does not have a save version and can't be upgraded.")
