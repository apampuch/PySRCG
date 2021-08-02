# noinspection PyUnresolvedReferences
import json

from src.CharData.character import *
from src.Tabs.attributes_tab import *
from src.Tabs.augments_tab import *
from src.Tabs.background_tab import *
from src.Tabs.decking_tab import *
from src.Tabs.gear_tab import GearTab
from src.Tabs.items_tab import *
from src.Tabs.karma_tab import KarmaTab
from src.Tabs.magic_tab import *
from src.Tabs.rigging_tab import RiggingTab
from src.Tabs.setup_tab import *
from src.Tabs.skills_tab import SkillsTab
from src.Tabs.top_menu import *
from src.utils import magic_tab_show_on_awakened_status

"""Idea: CalculatedGear items for things that depend on rating brackets"""
DEBUG = False

# TODO update the schema for ammo and accessories

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

        with open("src/Assets/SR3_Core.json", "r") as json_file:
            self.game_data = json.load(json_file)
            # pprint.pprint(self.game_data)
            # print(type(self.game_data))
            # print(self.game_data.keys())

    """Find a way to call this when loading"""
    def on_tab_changed(self, event):
        # overly complicated way to get the current tab
        # because everything in tkinter is overly complicated the more I look at it
        current_tab = self.select()
        current_tab = current_tab.replace(".!app.", "")
        current_tab = self.children[current_tab]
        current_tab.on_switch()

        app_data.app_character.statblock.gen_mode.update_karma_label(current_tab)


class TopBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.cash_label = ttk.Label(self, text=app_data.app_character.statblock.cash_str)

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


def main():
    app_data.root = Tk()
    # setup top menu
    app_data.app_character = Character()
    menu = TopMenu(app_data.root)
    app_data.root.configure(menu=menu)

    print("Setting the character!")

    # setup main window
    top_bar = TopBar(app_data.root)
    app_data.top_bar = top_bar
    app_data.window = App(app_data.root, top_bar)

    setup_tab = SetupTab(app_data.window)
    attributes_tab = AttributesTab(app_data.window)
    background_tab = BackgroundTab(app_data.window)
    skills_tab = SkillsTab(app_data.window)
    gear_tab = GearTab(app_data.window)#ItemsTab(app_data.window)
    magic_tab = MagicTab(app_data.window)
    augments_tab = AugmentsTab(app_data.window)
    decking_tab = DeckingTab(app_data.window)
    rigging_tab = RiggingTab(app_data.window)
    karma_tab = KarmaTab(app_data.window)

    top_bar.pack(fill=X)
    app_data.window.add(setup_tab, text="Character Setup")
    app_data.window.add(attributes_tab, text="Attributes")
    app_data.window.add(background_tab, text="Background")
    app_data.window.add(skills_tab, text="Skills")
    app_data.window.add(gear_tab, text="Gear")
    app_data.window.add(magic_tab, text="Magic")
    app_data.window.add(augments_tab, text="Augments")
    app_data.window.add(decking_tab, text="Decking")
    app_data.window.add(rigging_tab, text="Rigging")
    app_data.window.add(karma_tab, text="Karma")
    app_data.window.pack(fill=BOTH, expand=YES)

    magic_tab_show_on_awakened_status(app_data)

    post_setup(attributes_tab)
    app_data.root.mainloop()


if __name__ == "__main__":
    main()
