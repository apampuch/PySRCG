from typing import List, Any


class StatMod:
    """
    Just about anything in the chargen could theoretically have a StatMod.
    StatMods are things that add or subtract from numeric values if they're equipped/attached/whatever.
    They are supposed to be ridiculously dynamic so expect them to be really buggy.
    """
    # do not ever fucking directly manipulate this
    # key should be a string formatted as "TYPE_ATTRIBUTE", attributes can be things like armor too
    # value should be a list of integers
    _all_stat_mods = {}

    @staticmethod
    def add_mod(key, value):
        """If the key does not exist, add a blank list. Then append to the list."""
        if key not in StatMod._all_stat_mods.keys():
            StatMod._all_stat_mods[key] = []
        StatMod._all_stat_mods[key].append(value)

    @staticmethod
    def add_mods(item):
        for key in item.mods.keys():
            value = item.mods[key]
            StatMod.remove_mod(key, value)

    @staticmethod
    def remove_mod(key, value):
        """Remove value from list if it exists."""
        if key not in StatMod._all_stat_mods.keys():
            return
        try:
            StatMod._all_stat_mods[key].remove(value)
            if len(StatMod._all_stat_mods[key]) == 0:
                del StatMod._all_stat_mods[key]
        except ValueError:
            print(value + " doesn't exist in mods!")

    @staticmethod
    def reset_all_mods():
        StatMod._all_stat_mods = {}

    @staticmethod
    def get_mod_total(key):
        """Total the mods for the given key."""
        total = 0
        if key not in StatMod._all_stat_mods.keys():
            return total

        for mod in StatMod._all_stat_mods[key]:
            total += mod

        return total

    @staticmethod
    def mod_count():
        return len(StatMod._all_stat_mods)
