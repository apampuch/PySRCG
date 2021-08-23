from collections import OrderedDict
from copy import deepcopy

"""
These are all of the functions that should be used to upgrade a save file from one version to the next.
When a save from an older version is loaded, the current version should be found, then the following functions
called consecutively until the save is upgraded to the latest version.
"""

# TODO test
def v0_1_to_v0_2(save_file):
    """
    v0.1 -> v0.2: add Ammunition section
    don't bother moving ammo from items to ammo since nobody's actually using this yet
    """
    save_file["ammunition"] = []
    save_file["save_version"] = 0.2

# TODO test
def v0_2_to_v0_3(save_file):
    """
    v0.2 -> v0.3: add misc_weapon_accessories section, move accessories from items to weapon accessories as a test
    change other_accessories to misc_vehicle_accessories
    """
    save_file["misc_vehicle_accessories"] = deepcopy(save_file["other_accessories"])
    del save_file["other_accessories"]
    save_file["misc_weapon_accessories"] = []
    save_file["save_version"] = 0.3


"""
Use an ordered _dict to store these. 
"""
upgrade_funcs = OrderedDict()
upgrade_funcs[0.1] = v0_1_to_v0_2
upgrade_funcs[0.2] = v0_2_to_v0_3


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
