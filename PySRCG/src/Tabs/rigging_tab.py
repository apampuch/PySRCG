from tkinter import *
from tkinter import ttk

from src import app_data
from src.Tabs.vehicle_accessories_tab import VehicleAccessoriesTab
from src.Tabs.vehicle_buy_tab import VehicleBuyTab


class RiggingTab(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.vehicle_buy_tab = VehicleBuyTab(parent, "Buy", "Sell")
        self.vehicle_accessories_tab = VehicleAccessoriesTab(parent, "Buy", "Sell")
        # self.vehicle_custom_tab = None

        self.bind("<<NotebookTabChanged>>", app_data.window.on_tab_changed)

        self.add(self.vehicle_buy_tab, text="Vehicles")
        self.add(self.vehicle_accessories_tab, text="Accessories")
        # self.add(self.vehicle_custom_tab, text="Customization")

    def on_switch(self):
        self.vehicle_buy_tab.on_switch()
        self.vehicle_accessories_tab.on_switch()

    def load_character(self):
        self.vehicle_buy_tab.load_character()
        self.vehicle_accessories_tab.load_character()
