# noinspection PyUnresolvedReferences
import json
import pprint

from pathlib import Path

from src.CharData.character import *
from src.Tabs.Attributes.attributes_tab import *
from src.Tabs.Augments.augments_tab import *
from src.Tabs.Background.background_tab import BackgroundTab
from src.Tabs.Background.edges_flaws_tab import EdgesFlawsTab
from src.Tabs.Background.personal_info_tab import *
from src.Tabs.Decking.decking_tab import *  # imports app_data
from src.Tabs.Gear.ammo_tab import AmmoTab
from src.Tabs.Gear.armor_equip_tab import ArmorEquipTab
from src.Tabs.Gear.firearm_accessories_tab import FirearmAccessoriesTab
from src.Tabs.Gear.items_tab import ItemsTab
from src.Tabs.Gear.wireless_tab import WirelessTab
from src.Tabs.Rigging.vehicle_accessories_tab import VehicleAccessoriesTab
from src.Tabs.Rigging.vehicle_buy_tab import VehicleBuyTab
from src.Tabs.karma_tab import KarmaTab
from src.Tabs.Magic.magic_tab import *  # imports app_data
from src.Tabs.Setup.setup_tab import *
from src.Tabs.Skills.skills_tab import SkillsTab
from src.Tabs.container_tab import ContainerTab
from src.Tabs.top_menu import *  # imports app_data
from src.utils import magic_tab_show_on_awakened_status

DEBUG = False

# TODO implement name/string variables for items, like Activesoft (skill)

# TODO try to implement Improved Concealability (SR3, p291) for Surveillance Measures items. You'll need to be able to
#  set the UI textbox to 0 to do this, and only for those things you allow to be 0.

# TODO setup modular items when we get to Man and Machine (possibly sooner)


class App(ttk.Notebook):
    def __init__(self, parent, top_bar, **kw):
        super().__init__(parent, height=500, width=800, **kw)
        # self.character = character
        self.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.top_bar = top_bar
        self.game_data = None
        self.LOAD_DEBUG = False

        self.load_game_data()

    def on_tab_changed(self, event):
        # overly complicated way to get the current tab
        # because everything in tkinter is overly complicated the more I look at it
        current_tab = self.select()
        current_tab = current_tab.replace(".!app.", "")
        current_tab = self.children[current_tab]
        current_tab.on_switch()

        app_data.app_character.statblock.gen_mode.update_karma_label(current_tab)

    def load_game_data(self):
        self.game_data = {}

        for filename in SourcesWindow.selected_source_files:
            full_path = SourcesWindow.source_directory / filename
            with open(full_path, "r") as json_file:
                self.game_data.update(json.load(json_file))

                # load debug flag
                if self.LOAD_DEBUG:
                    pprint.pprint(self.game_data)
                    print(type(self.game_data))
                    print(self.game_data.keys())

        # cleanup unnecessary data
        clean_tags = ["book_abbr", "file_version", "schema_version", "book"]
        for tag in clean_tags:
            if tag in self.game_data:
                del self.game_data[tag]


class TopBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.cash_label = ttk.Label(self)

        # setup update events
        app_data.cash_update_events.append(self.update_cash_text)

        # karma label and bar
        self.karma_frame = Frame(self)
        self.karma_fraction = StringVar()
        self.karma_fraction.set("8/10")
        self.karma_label = Label(self.karma_frame, textvariable=self.karma_fraction)
        self.karma_bar = ttk.Progressbar(self.karma_frame)
        self.cheat_button = ttk.Button(self, text="Rules On")

        # packs
        options = {"side": LEFT, "expand": True}
        self.cash_label.pack(options)
        self.karma_frame.pack(options)
        self.cheat_button.pack(options)

        self.karma_label.pack(options)
        self.karma_bar.pack(options)

    def update_cash_text(self):
        self.cash_label.config(text=app_data.app_character.statblock.cash_str)

    # workaround for things that aren't explicitly in the priority system
    def update_karma_bar(self, numer, denom, dbg_source):
        if DEBUG:
            print("Updating from: " + dbg_source)
        self.karma_fraction.set("{}/{}".format(numer, denom))


def post_setup(attri_tab):
    """Things we need to do after initializing all tabs and classes."""
    attri_tab.calculate_total()


def make_tab(tab_type, name, container_types=None, container_names=None):
    """
    Creates a tab and adds it to the window.

    :type tab_type: type
    :type name: string
    :type container_types: List(type)
    :type container_names: List(str)
    """
    if container_types is None:
        container_types = []
    if container_names is None:
        container_names = []

    new_tab = tab_type(app_data.window)

    if hasattr(new_tab, "add_tabs"):
        child_tabs = []

        # make new tabs from types, assign new_tab as parent
        for type in container_types:
            child_tabs.append(type(app_data.window))

        new_tab.add_tabs(child_tabs, container_names)

    app_data.window.add(new_tab, text=name)
    return new_tab


def main():
    app_data.root = Tk()

    # setup top menu
    app_data.menu = TopMenu(app_data.root)
    app_data.root.configure(menu=app_data.menu)

    # setup config and stuff
    SourcesWindow.first_setup()

    # setup main window
    top_bar = TopBar(app_data.root)
    app_data.top_bar = top_bar
    app_data.window = App(app_data.root, top_bar)

    # setup character
    # this has to be done after setting up the window
    # if it's done before, the character will think that there is no window
    app_data.app_character = Character()

    # update top bar cash text
    top_bar.update_cash_text()

    setup_tab = make_tab(SetupTab, "Character Setup")
    attributes_tab = make_tab(AttributesTab, "Attributes")
    background_tab = make_tab(BackgroundTab, "Background",
                              [PersonalInfoTab, EdgesFlawsTab],
                              ["Personal Info", "Edges & Flaws"])
    skills_tab = make_tab(SkillsTab, "Skills")
    gear_tab = make_tab(ContainerTab, "Gear",
                        [ItemsTab, AmmoTab, FirearmAccessoriesTab, ArmorEquipTab, WirelessTab],
                        ["Items", "Ammo", "Firearm Accessories", "Armor", "Wireless"])
    magic_tab = make_tab(MagicTab, "Magic")     # this one has its own tab because it needs to do special things
    augments_tab = make_tab(ContainerTab, "Augments",
                            [CyberwareTab, BiowareTab],
                            ["Cyberware", "Bioware"])
    decking_tab = make_tab(DeckingTab, "Decking")
    rigging_tab = make_tab(ContainerTab, "Rigging",
                           [VehicleBuyTab, VehicleAccessoriesTab],
                           ["Vehicles", "Accessories"])
    karma_tab = make_tab(KarmaTab, "Karma")

    top_bar.pack(fill=X)
    app_data.window.pack(fill=BOTH, expand=YES)

    magic_tab_show_on_awakened_status(app_data)

    post_setup(attributes_tab)
    app_data.root.mainloop()


if __name__ == "__main__":
    main()
