from tkinter import ttk

from src import app_data
from src.Tabs.Gear.ammo_tab import AmmoTab
from src.Tabs.Gear.armor_equip_tab import ArmorEquipTab
from src.Tabs.Gear.items_tab import ItemsTab
from src.Tabs.Gear.firearm_accessories_tab import FirearmAccessoriesTab
from src.Tabs.Gear.wireless_tab import WirelessTab


class GearTab(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.items_tab = ItemsTab(parent)
        self.ammo_tab = AmmoTab(parent)
        self.weapon_accessories_tab = FirearmAccessoriesTab(parent)
        self.armor_equip_tab = ArmorEquipTab(parent)
        self.wireless_tab = WirelessTab(parent)

        self.bind("<<NotebookTabChanged>>", app_data.window.on_tab_changed)

        self.add(self.items_tab, text="Items")
        self.add(self.ammo_tab, text="Ammo")
        self.add(self.weapon_accessories_tab, text="Weapon Acessories")
        self.add(self.armor_equip_tab, text="Armor")
        self.add(self.wireless_tab, text="Wireless")

    def on_switch(self):
        self.items_tab.on_switch()
        self.ammo_tab.on_switch()
        self.weapon_accessories_tab.on_switch()
        self.armor_equip_tab.on_switch()
        self.wireless_tab.on_switch()

    def load_character(self):
        self.items_tab.load_character()
        self.ammo_tab.load_character()
        self.weapon_accessories_tab.load_character()
        self.armor_equip_tab.load_character()
        self.wireless_tab.load_character()
