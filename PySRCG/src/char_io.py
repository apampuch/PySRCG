import json
import os.path
import tempfile
from tkinter import filedialog
from typing import TextIO

from src.CharData.augment import Cyberware
from src.CharData.character import *
from src.CharData.complex_form import ComplexForm
from src.CharData.contact import Contact
from src.CharData.currency import Currency
from src.CharData.deck import Deck
from src.CharData.echo import Echo
from src.CharData.edge_flaw import EdgeFlaw
from src.CharData.firearm_accessory import FirearmAccessory
from src.CharData.gear import Gear
from src.CharData.lifestyle import SimpleLifestyle, AdvancedLifestyle
from src.CharData.power import Power
from src.CharData.program import Program
from src.CharData.race import all_races
from src.CharData.skill import Skill
from src.CharData.spell import Spell
from src.CharData.tradition import Tradition
from src.CharData.vehicle import Vehicle
from src.CharData.vehicle_accessory import VehicleAccessory
from src.CharData.wireless_accesory import WirelessAccessory
from src.GenModes.finalized import Finalized
from src.GenModes.priority import Priority
from src.save_version_upgrade import upgrade_funcs
from src.utils import magic_tab_show_on_awakened_status

SAVE_VERSION = 0.3

gen_mode_dict = {
    "priority": Priority,
    "finalized": Finalized
}


def new_char(tabs):
    # set character
    app_data.app_character = Character()

    # add default currency
    app_data.app_character.statblock.currencies.append(
        Currency("Miscellaneous Currency",
                 "Other",
                 "Miscellaneous",
                 False,
                 balance=app_data.app_character.statblock.gen_mode.get_generated_value("resources"),
                 permanent=True))

    # add freebie contacts
    app_data.app_character.contacts = [Contact("Freebie 1", "", "", 1, "", "", ""),
                                       Contact("Freebie 2", "", "", 1, "", "", "")]

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
        with __make_dummy(character) as dummy:
            with open(character.file_path, "w") as file:
                dummy.seek(0)
                file.write(dummy.read())


def save_as(character: Character):
    file: TextIO
    with __make_dummy(character) as dummy:
        try:
            file_types = [("JSON", ".json"), ("All Files", ".*")]
            with filedialog.asksaveasfile(filetypes=file_types, defaultextension=".json") as file:
                # if it crashes here you will lose your save
                # there should be no reason for that barring hardware issues
                dummy.seek(0)
                file.write(dummy.read())
        except AttributeError:
            print("Nothing saved.")
            raise
        except Exception:
            print("Nothing saved, now throwing error")
            raise


def __make_dummy(character: Character):
    """
    Makes a dummy file. ALWAYS CALL WITH "WITH AS"
    :param character: character to write
    :return: dummy file
    """
    dummy = tempfile.NamedTemporaryFile("w+")
    serialized_character = character.serialize()
    serialized_character["save_version"] = SAVE_VERSION
    json.dump(serialized_character, dummy, indent=2)
    return dummy


# def load(set_character: 'function', tabs: 'function'):
def load(tabs):
    file: TextIO
    try:
        with filedialog.askopenfile() as file:
            character_dict = json.load(file)
            new_character = Character()

            # check if we need to upgrade
            # if so, perform all upgrade functions from where we need to start to the end
            try:
                if character_dict["save_version"] in upgrade_funcs:
                    for key in upgrade_funcs:
                        # check if the version is greater than or equal
                        if character_dict["save_version"] == key:
                            upgrade_funcs[key](character_dict)
            except ValueError:
                print("Save file does not have a version. This save file can't be used, please manually recreate it.")

            # set race
            race_str = character_dict["statblock"]["race"]
            new_character.statblock.race = all_races[race_str]
            new_character.statblock.base_attributes = character_dict["statblock"]["base_attributes"]
            # new_character.statblock.cash = character_dict["statblock"]["cash"]

            # set genmode
            gen_mode_key = character_dict["statblock"]["gen_mode"]["type"]

            # only do purchased magic points if it's not finalized
            if gen_mode_key != "finalized":
                new_character.statblock.gen_mode = \
                    gen_mode_dict[gen_mode_key](character_dict["statblock"]["gen_mode"]["data"],
                                                purchased_magic_points=character_dict
                                                ["statblock"]["gen_mode"]["purchased_magic_points"])
            else:
                new_character.statblock.gen_mode = \
                    gen_mode_dict[gen_mode_key](character_dict["statblock"]["gen_mode"]["data"])

            new_character.statblock.gen_mode.setup_ui_elements()

            # convert dicts to item objects and add to inventory
            for lifestyle in character_dict["lifestyles"]:
                lifestyle_type = lifestyle["type"]
                del lifestyle["type"]
                if lifestyle_type == "Simple":
                    lifestyle_obj = SimpleLifestyle(**lifestyle)
                elif lifestyle_type == "Advanced":
                    lifestyle_obj = AdvancedLifestyle(**lifestyle)
                else:
                    raise ValueError('Lifestyle type must be "Simple" or "Advanced"!')

                new_character.lifestyles.append(lifestyle_obj)

            # new
            for contact in character_dict["contacts"]:
                contact_obj = Contact(**contact)
                new_character.contacts.append(contact_obj)

            for currency in character_dict["statblock"]["currencies"]:
                currency_obj = Currency(**currency)
                new_character.statblock.currencies.append(currency_obj)

            for item in character_dict["statblock"]["inventory"]:
                item_obj = Gear(**item)
                new_character.statblock.inventory.append(item_obj)

            for ammo in character_dict["statblock"]["ammunition"]:
                ammo_obj = Gear(**ammo)
                new_character.statblock.ammunition.append(ammo_obj)

            for firearm_accessory in character_dict["statblock"]["misc_firearm_accessories"]:
                firearm_accessory_obj = FirearmAccessory(**firearm_accessory)
                new_character.statblock.misc_firearm_accessories.append(firearm_accessory_obj)

            for wireless_accessory in character_dict["statblock"]["misc_wireless_accessories"]:
                wireless_accessory_obj = WirelessAccessory(**wireless_accessory)
                new_character.statblock.misc_wireless_accessories.append(wireless_accessory_obj)

            for edge_flaw in character_dict["statblock"]["edges_flaws"]:
                edge_flaw_obj = EdgeFlaw(**edge_flaw)
                if "mods" in edge_flaw_obj.properties:
                    for key in edge_flaw_obj.properties["mods"].keys():
                        value = edge_flaw_obj.properties["mods"][key]
                        StatMod.add_mod(key, value)
                new_character.statblock.edges_flaws.append(edge_flaw_obj)

            # add skills
            for skill in character_dict["statblock"]["skills"]:
                skill_obj = Skill(**skill)
                new_character.statblock.skills.append(skill_obj)

            # add spells
            for spell in character_dict["statblock"]["spells"]:
                spell_obj = Spell(**spell)
                new_character.statblock.spells.append(spell_obj)

            # add cyberware
            for cyber in character_dict["statblock"]["cyberware"]:
                cyber_obj = Cyberware(**cyber)
                # add mods
                if "mods" in cyber_obj.properties:
                    for key in cyber_obj.properties["mods"].keys():
                        value = cyber_obj.properties["mods"][key]
                        StatMod.add_mod(key, value)
                new_character.statblock.cyberware.append(cyber_obj)

            # add powers
            for power in character_dict["statblock"]["powers"]:
                power_obj = Power(**power)                # add mods
                if "mods" in power_obj.properties:
                    for key in power_obj.properties["mods"].keys():
                        value = power_obj.properties["mods"][key]
                        StatMod.add_mod(key, value)
                new_character.statblock.powers.append(power_obj)

            # add decks
            for deck in character_dict["statblock"]["decks"]:
                # may need to recurse and add programs and parts
                deck_obj = Deck(**deck)
                new_character.statblock.decks.append(deck_obj)

            # add vehicles
            for vehicle in character_dict["statblock"]["vehicles"]:
                # may need to recurse and add programs and parts
                vehicle_obj = Vehicle(**vehicle)
                new_character.statblock.vehicles.append(vehicle_obj)

            # add vehicle accessories
            for vehicle_accessory in character_dict["statblock"]["misc_vehicle_accessories"]:
                # may need to recurse and add programs and parts
                vehicle_accessory_obj = VehicleAccessory(**vehicle_accessory)
                new_character.statblock.misc_vehicle_accessories.append(vehicle_accessory_obj)

            # add programs
            for other_program in character_dict["statblock"]["other_programs"]:
                # may need to recurse and add programs and parts
                program_obj = Program(**other_program)
                new_character.statblock.other_programs.append(program_obj)

            # add complex forms
            for complex_form in character_dict["statblock"]["complex_forms"]:
                complex_form_obj = ComplexForm(**complex_form)
                new_character.statblock.complex_forms.append(complex_form_obj)

            # add echoes
            for echo in character_dict["statblock"]["echoes"]:
                echo_obj = Echo(**echo)
                new_character.statblock.echoes.append(echo_obj)

            # add tradition and aspect
            new_character.statblock.awakened = character_dict["statblock"]["awakened"]
            new_character.statblock.tradition = \
                Tradition(**character_dict["statblock"]["tradition"]) if character_dict["statblock"]["tradition"] is not None else None
            new_character.statblock.aspect = character_dict["statblock"]["aspect"]
            new_character.statblock.focus = character_dict["statblock"]["focus"]

            # set background info
            new_character.name.set(character_dict["name"])
            new_character.real_name.set(character_dict["real_name"])
            new_character.street_names.set(character_dict["street_names"])

            new_character.sex.set(character_dict["sex"])
            new_character.height.set(character_dict["height"])
            new_character.weight.set(character_dict["weight"])
            new_character.hair.set(character_dict["hair"])
            new_character.eyes.set(character_dict["eyes"])
            new_character.appearance.set(character_dict["appearance"])
            new_character.archetype.set(character_dict["archetype"])

            new_character.birthdate.set(character_dict["birthdate"])
            new_character.birthplace.set(character_dict["birthplace"])
            new_character.birth_notes.set(character_dict["birth_notes"])

            new_character.notes.set(character_dict["notes"])
            new_character.creator.set(character_dict["creator"])

            # set otaku
            new_character.statblock.otaku = character_dict["statblock"]["otaku"]
            new_character.statblock.runt_otaku = character_dict["statblock"]["runt_otaku"]
            new_character.statblock.otaku_path = character_dict["statblock"]["otaku_path"]

            # set character
            app_data.app_character = new_character

            # setup top bar
            app_data.on_cash_updated()

            # setup each tab after setting up character data
            for tab in tabs():
                tab.load_character()

            app_data.window.on_tab_changed(None)  # slightly hacky but it makes the bar update
            magic_tab_show_on_awakened_status(app_data)
            app_data.decking_tab.show_hide_tabs(app_data.app_character.statblock.otaku)

    except AttributeError as e:
        if "__enter__" in str(e):
            print("Nothing opened")
        else:
            raise e
