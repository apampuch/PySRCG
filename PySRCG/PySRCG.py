# noinspection PyUnresolvedReferences
import json

from src.Tabs.Attributes.attributes_tab import *
from src.Tabs.Augments.augments_tab import *
from src.Tabs.Augments.bioware_tab import BiowareTab
from src.Tabs.Augments.cyberware_tab import CyberwareTab
from src.Tabs.Background.background_tab import BackgroundTab
from src.Tabs.Background.banking_tab import BankingTab
from src.Tabs.Background.contacts_tab import ContactsTab
from src.Tabs.Background.edges_flaws_tab import EdgesFlawsTab
from src.Tabs.Background.lifestyles_tab import LifestylesTab
from src.Tabs.Background.personal_info_tab import *
from src.Tabs.Decking.complex_forms_tab import ComplexFormsTab
from src.Tabs.Decking.deck_buy_tab import DeckBuyTab
from src.Tabs.Decking.decking_tab import *  # imports app_data
from src.Tabs.Decking.frames_tab import FramesTab
from src.Tabs.Decking.otaku_tab import OtakuTab
from src.Tabs.Decking.persona_tab import PersonaTab
from src.Tabs.Decking.programs_tab import ProgramsTab
from src.Tabs.Decking.submersion_tab import SubmersionTab
from src.Tabs.Gear.ammo_tab import AmmoTab
from src.Tabs.Gear.armor_equip_tab import ArmorEquipTab
from src.Tabs.Gear.firearm_accessories_tab import FirearmAccessoriesTab
from src.Tabs.Gear.gear_tab import GearTab
from src.Tabs.Gear.items_tab import ItemsTab
from src.Tabs.Gear.wireless_tab import WirelessTab
from src.Tabs.Magic.foci_tab import FociTab
from src.Tabs.Magic.magic_background_tab import MagicBackgroundTab
from src.Tabs.Magic.powers_tab import PowersTab
from src.Tabs.Magic.spells_tab import SpellsTab
from src.Tabs.Rigging.rigging_tab import RiggingTab
from src.Tabs.Rigging.vehicle_accessories_tab import VehicleAccessoriesTab
from src.Tabs.Rigging.vehicle_buy_tab import VehicleBuyTab
from src.Tabs.karma_tab import KarmaTab
from src.Tabs.Magic.magic_tab import *  # imports app_data
from src.Tabs.Setup.setup_tab import *
from src.Tabs.Skills.skills_tab import SkillsTab
from src.Tabs.tab import Tab
from src.Tabs.top_menu import *  # imports app_data
from src.game_data import GameData
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
        self.LOAD_DEBUG = False

        self.load_game_data()

    @staticmethod
    def load_game_data():
        app_data.game_data = GameData()

        for filename in SourcesWindow.selected_source_files:
            full_path = SourcesWindow.source_directory / filename
            with open(full_path, "r") as json_file:
                app_data.game_data.add(json.load(json_file))

    def on_tab_changed(self, event):
        # overly complicated way to get the current tab
        # because everything in tkinter is overly complicated the more I look at it
        current_tab: NotebookTab | ContainerTab | Widget
        tab_string: str
        tab_string = self.select()
        tab_string = tab_string.replace(".!app.", "")
        current_tab = self.children[tab_string]
        current_tab.update_karma_bar()
        current_tab.on_switch()


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
    def update_karma_label(self, numer, denom, dbg_source):
        if DEBUG:
            print("Updating from: " + dbg_source)
        self.karma_fraction.set("{}/{}".format(numer, denom))


def post_setup(attributes_tab):
    """Things we need to do after initializing all tabs and classes."""
    attributes_tab.calculate_total()


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
        for con_type in container_types:
            child_tabs.append(con_type(new_tab))

        new_tab.add_tabs(child_tabs, container_names)

    app_data.window.add(new_tab, text=name)
    return new_tab


def main():
    app_data.root = Tk()
    Tab.setup_always_zero()

    # setup top menu
    app_data.menu = TopMenu(app_data.root)
    app_data.root.configure(menu=app_data.menu)

    # setup config and stuff
    SourcesWindow.first_setup()

    # setup main window
    top_bar = TopBar(app_data.root)
    app_data.top_bar = top_bar
    app_data.window = App(app_data.root, top_bar)

    app_data.setup_tab = make_tab(SetupTab, "Character Setup")
    app_data.attributes_tab = make_tab(AttributesTab, "Attributes")
    app_data.background_tab = make_tab(BackgroundTab, "Background",
                                       [PersonalInfoTab, EdgesFlawsTab, BankingTab, LifestylesTab, ContactsTab],
                                       ["Personal Info", "Edges & Flaws", "Banking", "Lifestyles", "Contacts"])
    app_data.skills_tab = make_tab(SkillsTab, "Skills")
    app_data.gear_tab = make_tab(GearTab, "Gear",
                                 [ItemsTab, AmmoTab, FirearmAccessoriesTab, ArmorEquipTab, WirelessTab],
                                 ["Items", "Ammo", "Firearm Accessories", "Armor", "Wireless"])
    app_data.magic_tab = make_tab(MagicTab, "Magic",
                                  [MagicBackgroundTab, SpellsTab, PowersTab, FociTab],
                                  ["Background", "Spells", "Powers", "Foci"])
    app_data.augments_tab = make_tab(AugmentsTab, "Augments",
                                     [CyberwareTab, BiowareTab],
                                     ["Cyberware", "Bioware"])
    app_data.decking_tab = make_tab(DeckingTab, "Decking",
                                    [DeckBuyTab, ProgramsTab, PersonaTab, OtakuTab, ComplexFormsTab, SubmersionTab, FramesTab],
                                    ["Hardware", "Software", "Persona", "Otaku", "Complex Forms", "Submersion", "Frames"])
    app_data.rigging_tab = make_tab(RiggingTab, "Rigging",
                                    [VehicleBuyTab, VehicleAccessoriesTab],
                                    ["Vehicles", "Accessories"])
    app_data.karma_tab = make_tab(KarmaTab, "Karma")

    # setup character
    # this has to be done after setting up the window
    # if it's done before, the character will think that there is no window
    char_io.new_char(lambda: app_data.root.winfo_children()[2].winfo_children())

    # update top bar cash text
    top_bar.update_cash_text()

    top_bar.pack(fill=X)
    app_data.window.pack(fill=BOTH, expand=YES)

    magic_tab_show_on_awakened_status(app_data)

    post_setup(app_data.attributes_tab)
    app_data.setup_tab.gen_mode_var.set("Priority")  # do this here so we can set priority without triggering any errors
    app_data.root.mainloop()


if __name__ == "__main__":
    main()
