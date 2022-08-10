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
    tier: int
    level_costs = (0, 100, 1000, 5000, 10000, 100000)
    type = "Simple"

    @staticmethod
    def fromAdvanced(a):
        """
        @type a: AdvancedLifestyle
        """
        # find closest lifestyle
        tier = -1
        diff = 99999999999999999999999999999
        for i in range(0, len(SimpleLifestyle.level_costs)):
            new_diff = abs(a.cost() - SimpleLifestyle.level_costs[i])
            if new_diff < diff:
                tier = i
                diff = new_diff

        return SimpleLifestyle(a.name, a.residence, a.permanent, a.month, a.year, a.LTG, a.description, a.notes, tier)

    def __init__(self, name, residence, permanent, month, year, LTG, description, notes, tier):
        super().__init__(name, residence, permanent, month, year, LTG, description, notes)
        if tier >= len(SimpleLifestyle.level_costs):
            raise ValueError(f"{tier} not a valid tier of lifestyle!")
        self.tier = tier

    def cost(self):
        return SimpleLifestyle.level_costs[self.tier]


class AdvancedLifestyle(Lifestyle):
    type = "Advanced"
    costs = [1, 15, 30, 45, 60, 70, 85, 100, 250, 400, 550, 700, 850, 1000, 1650, 2350, 3000, 3650, 4350, 5000, 5850,
             6650, 7500, 8350, 9150, 10000, 25000, 40000, 55000, 70000, 85000, 100000, 125000, 150000]

    @staticmethod
    def fromSimple(s):
        """
        @type s: SimpleLifestyle
        """
        return AdvancedLifestyle(s.name, s.residence, s.permanent, s.month, s.year, s.LTG, s.description, s.notes,
                                 s.tier, s.tier, s.tier, s.tier, s.tier, s.tier)

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
        total = self.area + self.comforts + self.entertainment + self.furnishings + self.security + self.space - 1
        return AdvancedLifestyle.costs[total]
