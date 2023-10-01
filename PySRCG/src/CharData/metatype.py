from copy import copy


class Metatype(object):
    def __init__(self, name, point_cost, **kwargs):
        self.name = name
        self.metatype_attributes = kwargs["metatype_attributes"]

        # zero everything that we don't already have
        for key in ("body", "quickness", "strength", "charisma", "intelligence", "willpower"):
            if key not in self.metatype_attributes:
                self.metatype_attributes[key] = 0

        self.karma_div = kwargs["karma_div"] if "karma_div" in kwargs else 20  # the divisor of good karma to karma pool
        self.point_cost = point_cost

    def metatype_slider_minimum(self, key):
        if key not in self.metatype_attributes:
            return 0
        """Used to set the minimum for the attributes tab."""
        return max(1, 1 - self.metatype_attributes[key])

    def serialize(self):
        return self.__dict__
