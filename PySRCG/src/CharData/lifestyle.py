from abc import ABC, abstractmethod


class Lifestyle(ABC):
    type = "INVALID"

    def __init__(self, name, residence, permanent, month, year, LTG, description, notes):
        self.name = name
        self.residence = residence
        self.permanent = permanent
        self.month = month
        self.year = year
        self.LTG = LTG
        self.description = description
        self.notes = notes

    @abstractmethod
    def cost(self):
        pass


class SimpleLifestyle(Lifestyle, ABC):
    level_cost_dict = {
        "Street (Free)": 0,
        "Squatter (¥100)": 100,
        "Low (¥1000)": 1000,
        "Middle (¥5000)": 5000,
        "High (¥10000)": 10000,
        "Luxury (¥100000)": 100000
    }
    type = "Simple"

    @staticmethod
    def fromAdvanced(a):
        """
        @type a: AdvancedLifestyle
        """
        return SimpleLifestyle(a.name, a.residence, a.permanent, a.month, a.year,
                               a.LTG, a.description, a.notes, "Street (Free)")

    def __init__(self, name, residence, permanent, month, year, LTG, description, notes, tier):
        super().__init__(name, residence, permanent, month, year, LTG, description, notes)
        if tier not in SimpleLifestyle.level_cost_dict:
            raise ValueError(f"{tier} not a valid tier of lifestyle!")
        self.tier = tier

    def cost(self):
        return SimpleLifestyle.level_cost_dict[self.tier]


class AdvancedLifestyle(Lifestyle):
    type = "Advanced"

    @staticmethod
    def fromSimple(s):
        """
        @type s: SimpleLifestyle
        """
        return AdvancedLifestyle(s.name, s.residence, s.permanent, s.month, s.year,
                               s.LTG, s.description, s.notes, 0, 0, 0, 0, 0, 0)

    # noinspection PyPep8Naming
    def __init__(self, name, residence, permanent, month, year, LTG, description, notes,
                 area, comforts, entertainment, furnishings, security, space):
        super().__init__(name, residence, permanent, month, year, LTG, description, notes)
        # define all the tiers for shit and lists for all the perks and hindrances

        self.area = area
        self.comforts = comforts
        self.entertainment = entertainment
        self.furnishings = furnishings
        self.security = security
        self.space = space

        self.perks = []
        self.hindrances = []

    def cost(self):
        total = self.area + self.comforts + self.entertainment + self.furnishings + self.security + self.space + 1
        total *= 15
        return total
