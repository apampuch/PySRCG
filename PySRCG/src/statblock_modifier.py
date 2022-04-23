import re


class StatMod:
    """
    Just about anything in the chargen could theoretically have a StatMod.
    StatMods are things that add or subtract from numeric values if they're equipped/attached/whatever.
    They are supposed to be ridiculously dynamic so expect them to be really buggy.
    """
    # do not ever fucking directly manipulate this
    # key should be a string formatted as "TYPE_ATTRIBUTE", attributes can be things like armor too
    # e.g "cyber_reaction" or "edge_strength"
    # value should be a list of integers
    _all_stat_mods = {}

    # if it's one of these:
    # Race
    # Cyber
    # Bio
    # put it in the correct column
    # otherwise put it in the other column

    @staticmethod
    def correct_key(key):
        # this checks that it matches two words separated by a single underscore
        # e.g. magic_body
        regex_check = r"^[^_]+_{1}[^_]+$"

        # this is used to substitute the first word
        regex_sub = r"^[^_]+_{1}"

        if not re.match(regex_check, key):
            raise ValueError(f"{key} is not a valid key.")

        # correct the key
        legit_prefixes = ("race_", "cyber_", "bio_")

        for prefix in legit_prefixes:
            if key.startswith(prefix):
                return key

        # replace prefix if not legit
        key = re.sub(regex_sub, "other_", key)

        return key

    @staticmethod
    def add_mod(key, value):
        """
        IF the key doesn't start with "race_", "cyber_", or "bio_", change the start to "other_"
        If the key does not exist, add a blank list.
        Then append to the list.
        """

        # correct the key so that anything that isn't a column in attributes_tab is "other"
        key = StatMod.correct_key(key)

        if key not in StatMod._all_stat_mods.keys():
            StatMod._all_stat_mods[key] = []
        StatMod._all_stat_mods[key].append(value)
        # print(StatMod._all_stat_mods)

    @staticmethod
    def add_mods(item):
        for key in item.mods.keys():
            value = item.mods[key]
            StatMod.remove_mod(key, value)

    @staticmethod
    def remove_mod(key, value):
        """Remove value from list if it exists."""
        key = StatMod.correct_key(key)

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
