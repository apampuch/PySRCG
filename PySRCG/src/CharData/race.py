class Race(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.racial_attributes = {}

        self.set_initial_base_attribute("body", kwargs)
        self.set_initial_base_attribute("quickness", kwargs)
        self.set_initial_base_attribute("strength", kwargs)
        self.set_initial_base_attribute("charisma", kwargs)
        self.set_initial_base_attribute("intelligence", kwargs)
        self.set_initial_base_attribute("willpower", kwargs)

        self.karma_div =  kwargs["karma_div"] if "karma_div" in kwargs else 20  # the divisor of good karma to karma pool

        all_races[name] = self

    def set_initial_base_attribute(self, key, kwargs):
        """Used by __init__ to setup base attributes"""
        if key in kwargs:
            self.racial_attributes[key] = kwargs[key]
        else:
            self.racial_attributes[key] = 0

    def racial_slider_minimum(self, key):
        """Used to set the minimum for the attributes tab."""
        return max(1, 1 - self.racial_attributes[key])

    def racial_max(self, key):
        return max(1, min(6, 6 + self.racial_attributes[key]))


all_races = {}

# add the other shit from page 56 later
Human = Race("Human", karma_div=10)
Dwarf = Race("Dwarf", body=1, strength=2, willpower=1)
Elf = Race("Elf", quickness=1, charisma=2)
Ork = Race("Ork", body=3, strength=2, charisma=-1, intelligence=-1)
Troll = Race("Troll", body=5, quickness=-1, strength=4, intelligence=-2, charisma=-2)
