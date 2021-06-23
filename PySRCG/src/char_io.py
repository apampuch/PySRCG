import src.app_data as app_data
import json
import os.path

from src.CharData.accessory import Accessory
from src.CharData.augment import Cyberware
from src.CharData.character import *
from src.CharData.deck import Deck
from src.CharData.gear import find_gear_by_dict_load
from src.CharData.power import Power
from src.CharData.program import Program
from src.CharData.race import all_races
from src.CharData.skill import Skill
from src.CharData.tradition import Tradition
from src.GenModes.priority import Priority
from src.GenModes.finalized import Finalized
from src.utils import magic_tab_show_on_awakened_status
from tkinter import filedialog
from typing import TextIO

from src.CharData.spell import Spell
from src.CharData.vehicle import Vehicle

gen_mode_dict = {
    "priority": Priority,
    "finalized": Finalized
}


def new_char(tabs):
    # set character
    app_data.app_character = Character()

    # setup top bar
    app_data.on_cash_updated()

    # setup the bare minimum so tab.load_character() doesn't crash
    app_data.app_character.name.set("")
    app_data.app_character.sex.set("Male")

    # setup each tab after setting up character data
    for tab in tabs():
        tab.load_character()

    app_data.window.on_tab_changed(None)  # slightly hacky but it makes the bar update
    magic_tab_show_on_awakened_status(app_data)


def save(character: Character):
    if not os.path.exists(character.file_path):
        save_as(character)
    else:
        with open(character.file_path, "w") as file:
            __write_file(file, character)


def save_as(character: Character):
    file: TextIO
    try:
        file_types = [("JSON", ".json"), ("All Files", ".*")]
        with filedialog.asksaveasfile(filetypes=file_types, defaultextension=".json") as file:
            __write_file(file, character)
    except AttributeError:
        print("Nothing saved")
        return


def __write_file(file, character: Character):
    print(file.name)
    # file.encoding = "utf-8"  # set encoding to utf-8 so things work everywhere
    character.file_path = file.name
    serialized_character = character.serialize()
    json.dump(serialized_character, file, indent=2)


# def load(set_character: 'function', tabs: 'function'):
def load(tabs):
    file: TextIO
    try:
        with filedialog.askopenfile() as file:
            d = json.load(file)
            new_character = Character()

            # set race
            race_str = d["statblock"]["race"]
            new_character.statblock.race = all_races[race_str]
            new_character.statblock.base_attributes = d["statblock"]["base_attributes"]
            new_character.statblock.cash = d["statblock"]["cash"]

            # set genmode
            gen_mode_key = d["statblock"]["gen_mode"]["type"]
            # PROBLEM: the args are only setup for a finalized thing
            new_character.statblock.gen_mode = gen_mode_dict[gen_mode_key](d["statblock"]["gen_mode"]["data"], all_races[race_str])

            # convert dicts to item objects and add to inventory
            for item in d["statblock"]["inventory"]:
                item_obj = find_gear_by_dict_load(item)
                new_character.statblock.inventory.append(item_obj)

            # add skills
            for skill in d["statblock"]["skills"]:
                skill_obj = Skill(**skill)
                new_character.statblock.skills.append(skill_obj)

            # add spells
            for spell in d["statblock"]["spells"]:
                spell_obj = Spell(**spell)
                new_character.statblock.spells.append(spell_obj)

            # add cyberware
            for cyber in d["statblock"]["cyberware"]:
                cyber_obj = Cyberware(**cyber)
                # check for mods
                if len(cyber_obj.mods.keys()) > 0:
                    print("stop here")
                new_character.statblock.cyberware.append(cyber_obj)

            # add powers
            for power in d["statblock"]["powers"]:
                power_obj = Power(**power)
                new_character.statblock.powers.append(power_obj)

            # add decks
            for deck in d["statblock"]["decks"]:
                # may need to recurse and add programs and parts
                deck_obj = Deck(**deck)
                new_character.statblock.decks.append(deck_obj)
                
            # add vehicles
            for vehicle in d["statblock"]["vehicles"]:
                # may need to recurse and add programs and parts
                vehicle_obj = Vehicle(**vehicle)
                new_character.statblock.vehicles.append(vehicle_obj)
                
            # add accessories
            for accessory in d["statblock"]["other_accessories"]:
                # may need to recurse and add programs and parts
                accessory_obj = Accessory(**accessory)
                new_character.statblock.other_accessories.append(accessory_obj)

            # add programs
            # TODO make it add stuff from all program containers
            for other_program in d["statblock"]["other_programs"]:
                # may need to recurse and add programs and parts
                program_obj = Program(**other_program)
                new_character.statblock.other_programs.append(program_obj)

            # add tradition and aspect
            new_character.statblock.awakened = d["statblock"]["awakened"]
            new_character.statblock.tradition = \
                Tradition(**d["statblock"]["tradition"]) if d["statblock"]["tradition"] is not None else None
            new_character.statblock.aspect = d["statblock"]["aspect"]
            new_character.statblock.focus = d["statblock"]["focus"]

            # set background info
            new_character.name.set(d["name"])
            new_character.sex.set(d["sex"])

            # set gen mode
            if d["statblock"]["gen_mode"]["type"] == "priority":
                new_character.statblock.gen_mode = Priority(d["statblock"]["gen_mode"]["data"])
                new_character.statblock.gen_mode.setup_ui_elements()
            else:
                print("{} is NYI".format(d["statblock"]["gen_mode"]["type"]))

            # set character
            app_data.app_character = new_character

            # setup top bar
            app_data.on_cash_updated()

            # setup each tab after setting up character data
            for tab in tabs():
                tab.load_character()

            app_data.window.on_tab_changed(None)  # slightly hacky but it makes the bar update
            magic_tab_show_on_awakened_status(app_data)

    except AttributeError as e:
        if "__enter__" in str(e):
            print("Nothing opened")
        else:
            raise e
