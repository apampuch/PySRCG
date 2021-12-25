from tkinter import IntVar
from typing import Dict

from src import app_data
from src.GenModes.priority import Priority
from src.app_data import on_cash_updated
from src.Tabs.Attributes.attributes_tab import AttributesTab
from src.CharData.race import Race
from src.statblock_modifier import StatMod


def add_if_not_there(_dict, key):
    """Used by Statblock.essence getter"""
    if key not in _dict.keys():
        _dict[key] = [0, 0]


class Statblock(object):
    base_attributes: Dict[str, int]
    __race: Race

    @property
    def cash(self):
        return self.__cash
    @cash.setter
    def cash(self, value):
        self.__cash = value
        self.cash_str = "¥{}".format(self.__cash)
        on_cash_updated()

    @property
    def awakened(self):
        return self.__awakened
    @awakened.setter
    def awakened(self, value):
        self.__awakened = value

        # callback magic tab
        app_data.window.nametowidget(".!app.!magictab").show_hide_tabs(self.awakened, self.tradition)

    @property
    def tradition(self):
        return self.__tradition
    @tradition.setter
    def tradition(self, value):
        self.__tradition = value

        # callback magic tab
        app_data.window.nametowidget(".!app.!magictab").show_hide_tabs(self.awakened, self.tradition)

    def __init__(self, race):
        self.__race = race
        self.base_attributes = {"body": 1,
                                "quickness": 1,
                                "strength": 1,
                                "charisma": 1,
                                "intelligence": 1,
                                "willpower": 1}

        # reset StatMods because those should be fresh with a new statblock, we add those in as we load a character
        # I may be wrong on where this needs to go though
        StatMod.reset_all_mods()

        # setup armor
        self.ballistic_armor = 0
        self.impact_armor = 0
        self.armor_quickness_penalty = 0
        self.armor_combat_pool_penalty = 0

        # always start with 6 essence
        self.base_attributes["essence"] = 6.0
        self.ess_ui_var = IntVar()  # this only exists so we can control the progress bar with the essence value
        self.power_points_ui_var = IntVar()  # same as above but for power points
        self.ess_ui_var.set(6)

        # setup gen mode
        self.gen_mode = Priority()

        # setup cash
        self.__cash = self.gen_mode.get_generated_value("resources")
        self.cash_str = "¥{}".format(self.__cash)

        # setup inventory
        self.inventory = []

        # setup ammo
        self.ammunition = []

        # setup weapon accessories
        self.misc_firearm_accessories = []

        # setup skills
        self.skills = []

        """
        self.awakened: Can either be None, "aspected", or "full"
        self.tradition: Shamanism, Hermetic, or Adept (in core)
        self.aspect: Conjurer, Sorcerer, Elementalist, etc. If self.awakened is None or "Full", it doesn't matter.
        """

        # setup awakened status
        self.__awakened = None
        self.__tradition = None
        self.aspect = None
        self.focus = None
        self.spells = []

        # setup cyberware
        self.cyberware = self.cyberware = []

        # setup adept powers
        self.powers = []
        self.bonus_power_points = 0

        # setup decks
        self.decks = []
            
        # setup vehicles
        self.vehicles = []
            
        # setup vehicle accessories
        self.misc_vehicle_accessories = []

        # setup miscellaneous programs
        self.other_programs = []

    def calculate_attribute(self, key):
        # take care of magic keys
        if key == "reaction":
            total = self.base_reaction
        elif key == "magic":
            total = self.magic
        elif key == "essence":
            # for cyber in self.cyberware:
            total = self.essence
        elif key == "initiative":
            total = 1
        else:
            total = self.base_attributes[key]
            
        # add racial attribute bonus
        if key in self.race.racial_attributes:
            total += self.race.racial_attributes[key]

        # add cyber bonus
        cyber_key = "cyber_" + key
        total += StatMod.get_mod_total(cyber_key)

        # add bio bonus
        bio_key = "bio_" + key
        total += StatMod.get_mod_total(bio_key)

        # add other bonus
        other_key = "other_" + key
        total += StatMod.get_mod_total(other_key)

        # can't be less than 1
        total = max(total, 1)

        return total

    def calculate_natural_attribute(self, key):
        # take care of magic keys
        if key == "reaction":
            return self.reaction
        elif key == "magic":
            return self.magic
        elif key == "essence":
            # for cyber in self.cyberware:
            return self.essence
        else:
            total = self.base_attributes[key]
            # add racial attribute bonus
            total += self.race.racial_attributes[key]

            # add bio bonus
            bio_key = "bio_" + key
            total += StatMod.get_mod_total(bio_key)

            # add other bonus
            other_key = "other_" + key
            total += StatMod.get_mod_total(other_key)

            # can't be less than 1
            total = max(total, 1)

            return total

    def calculate_armor_and_penalties(self, equipped_armors, equipped_helmet, equipped_shield):

        def extract_val_from_armor(armor, prop):
            return armor.properties[prop]

        # sorted by ballistic
        sorted_ballistic = sorted(equipped_armors, key=lambda x: extract_val_from_armor(x, "ballistic"), reverse=True)
        sorted_impact = sorted(equipped_armors, key=lambda x: extract_val_from_armor(x, "impact"), reverse=True)

        ballistic_combat_pool_penalty = 0
        impact_combat_pool_penalty = 0

        # pop the highest values for the inital values
        if len(sorted_ballistic) > 0:
            self.ballistic_armor = \
                self.armor_quickness_penalty = \
                ballistic_combat_pool_penalty = sorted_ballistic.pop(0).properties["ballistic"]
        else:
            self.ballistic_armor = \
                self.armor_quickness_penalty = 0

        if len(sorted_impact) > 0:
            self.impact_armor = \
                impact_combat_pool_penalty = sorted_impact.pop(0).properties["impact"]
        else:
            self.impact_armor = 0

        # iterate through the list of armor indices and add half
        # to get the rest for the quickness and combat pool penalties
        for i in sorted_ballistic:
            self.ballistic_armor += i.properties["ballistic"] // 2
            self.armor_quickness_penalty += i.properties["ballistic"]
            ballistic_combat_pool_penalty += i.properties["ballistic"]

        # add helmet and shield
        for i in sorted_ballistic:
            self.impact_armor += i.properties["impact"] // 2
            impact_combat_pool_penalty += i.properties["impact"]

        # calculate combat pool penalty
        ballistic_combat_pool_penalty = max(0, (ballistic_combat_pool_penalty - self.quickness))
        impact_combat_pool_penalty = max(0, (impact_combat_pool_penalty - self.quickness))

        self.armor_combat_pool_penalty = (ballistic_combat_pool_penalty + impact_combat_pool_penalty) // 2

        # calculate armor penalty
        self.armor_quickness_penalty = \
            max(0, self.armor_quickness_penalty - self.quickness)

    @property
    def race(self):
        return self.__race
    @race.setter
    def race(self, value: Race):
        old_race = self.__race

        # adjust the attribute values so that the slider position is the same
        # if above max, set to max
        for key in AttributesTab.base_attributes:
            attr_pos = self.base_attributes[key] - old_race.racial_slider_minimum(key)
            self.base_attributes[key] = attr_pos + value.racial_slider_minimum(key)

        self.__race = value

    ######################################
    # DICE POOLS, RETURNS NUMBER OF DICE #
    ######################################
    @property
    def combat_pool(self):
        # it shouldn't be possible to go below 0 combat pool
        return max(0, (self.quickness + self.intelligence + self.willpower) // 2 - self.armor_combat_pool_penalty)

    @property
    def astral_combat_pool(self):
        if self.awakened is None:
            return 0
        else:
            return (self.intelligence + self.charisma + self.willpower) // 2

    @property
    def control_pool(self):
        return self.reaction + 0  # TODO factor in VCR

    @property
    def hacking_pool(self):
        return (self.intelligence + 0) // 3  # TODO factor in MPCP

    @property
    def spell_pool(self):
        if self.awakened is None:
            return 0
        else:
            return (self.intelligence + self.willpower + self.magic) // 3

    #####################
    # ATTRIBUTE GETTERS #
    #####################
    @property
    def body(self):
        return self.calculate_attribute("body")

    @property
    def quickness(self):
        return self.calculate_attribute("quickness")

    @property
    def strength(self):
        return self.calculate_attribute("strength")

    @property
    def charisma(self):
        return self.calculate_attribute("charisma")

    @property
    def intelligence(self):
        return self.calculate_attribute("intelligence")

    @property
    def willpower(self):
        return self.calculate_attribute("willpower")

    @property
    def essence(self):
        essence_total = 6  # I am SURE there are races that have more essence

        fit_dict = self.make_fit_dict()

        # perform this complicated sum algorithm
        for item in fit_dict.values():
            line_total = item[1]
            line_total -= item[0]
            line_total = max(line_total, 0)
            essence_total -= line_total

        # set the essence UI control variable so it properly updates the UI
        self.ess_ui_var.set(essence_total)
        return essence_total

    # do we need this?
    @essence.setter
    def essence(self, value):
        self.base_attributes["essence"] = value

    def make_fit_dict(self):
        """
        Makes the fit _dict. This is for things like cybereyes and cyberears that can hold amounts of mods themselves.
        Fit _dict is as follows:
        SLOT_NAME: [AMOUNT_HOLDS, TOTAL_FIT]
        :return: A dictionary containing the values of free essence by slot.
        """
        fit_dict = {None: [0, 0]}

        for cyber in self.cyberware:
            # track things that cyberware holds
            if "holds" in cyber.properties:
                # cyber.properties["holds"]["type"] is the type of mod it holds, ["essence"] is the cost
                add_if_not_there(fit_dict, cyber.properties["holds"]["type"])
                fit_dict[cyber.properties["holds"]["type"]][0] += cyber.properties["holds"]["essence"]

            # track things that cyberware fits
            if "fits" in cyber.properties:
                add_if_not_there(fit_dict, cyber.properties["fits"])
                fit_dict[cyber.properties["fits"]][1] += cyber.properties["essence"]
            else:
                fit_dict[None][1] += cyber.properties["essence"]

        return fit_dict

    @property
    def base_reaction(self):
        return (self.quickness + self.intelligence) // 2

    # calculated attributes
    @property
    def reaction(self):
        return self.calculate_attribute("reaction")

    @property
    def initiative(self):
        return self.calculate_attribute("initiative")

    @property
    def magic(self):
        return int(self.essence)

    @property
    # power points from adept powers
    def power_points(self):
        total = 0
        for power in self.powers:
            total += power.properties["cost"]

        return total

    @property
    def total_power_points(self):
        return self.magic + self.bonus_power_points

    def serialize(self):
        """
        Serializes this into a _dict for turning into a json.
        """
        inventory = list(map(lambda x: x.serialize(), self.inventory))
        ammunition = list(map(lambda x: x.serialize(), self.ammunition))
        misc_firearm_accessories = list(map(lambda x: x.serialize(), self.misc_firearm_accessories))
        gen_mode = self.gen_mode.serialize()
        skills = list(map(lambda x: x.serialize(), self.skills))
        tradition = self.tradition.serialize() if self.tradition is not None else None
        spells = list(map(lambda x: x.serialize(), self.spells))
        cyberware = list(map(lambda x: x.serialize(), self.cyberware))
        # bioware = list(map(lambda x: x.serialize(), self.bioware))
        powers = list(map(lambda x: x.serialize(), self.powers))
        decks = list(map(lambda x: x.serialize(), self.decks))
        vehicles = list(map(lambda x: x.serialize(), self.vehicles))
        other_accessories = list(map(lambda x: x.serialize(), self.misc_vehicle_accessories))
        other_programs = list(map(lambda x: x.serialize(), self.other_programs))
        return {
            "race": self.__race.name,
            "base_attributes": self.base_attributes,
            "cash": self.__cash,
            "inventory": inventory,
            "ammunition": ammunition,
            "misc_firearm_accessories": misc_firearm_accessories,
            "gen_mode": gen_mode,
            "skills": skills,
            "spells": spells,
            "cyberware": cyberware,
            "powers": powers,
            "bonus_power_points": self.bonus_power_points,
            "awakened": self.awakened,
            "tradition": tradition,
            "aspect": self.aspect,
            "focus": self.focus,
            "decks": decks,
            "vehicles": vehicles,
            "other_programs": other_programs,
            "misc_vehicle_accessories": other_accessories
        }

    def pay_cash(self, amount, *args) -> bool:
        """
        Pays cash and returns true if we can afford it, false if we can't afford it
        :param amount: Amount we want to pay.
        :param args: Other args we pass in from outside that could stop us from buying it.
        :type args: bool[]
        """
        #
        will_pay = True
        for b in args:
            will_pay = will_pay and b

        if amount <= self.__cash and will_pay:
            self.cash -= amount
            return True
        else:
            return False
