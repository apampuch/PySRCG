from abc import ABC

from src.Tabs import Gear
from src.Tabs.notebook_tab import NotebookTab
from tkinter import *
from tkinter import ttk


class ArmorEquipTab(NotebookTab, ABC):

    def __init__(self, parent):
        super().__init__(parent)

        self.armor_list = []
        self.selected_armor_list = []

        self.shield_list = []
        self.selected_shield_list = []

        self.helmet_list = []
        self.selected_helmet_list = []

        # use a listbox for now and find a better way to do this
        self.instruction_label = ttk.Label(self, text="Highlighted armors are equipped. You may layer armors as per SR3 rules on page 285.")

        self.armor_listbox = Listbox(self, selectmode=MULTIPLE, activestyle=NONE, height=20)
        self.armor_listbox.bind("<<ListboxSelect>>", self.on_click_armor)
        self.armor_scroll_bar = Scrollbar(self, orient=VERTICAL, command=self.armor_listbox.yview)

        self.shield_listbox = Listbox(self, selectmode=SINGLE, activestyle=NONE, height=20)
        self.shield_listbox.bind("<<ListboxSelect>>", self.on_click_armor)
        self.shield_scroll_bar = Scrollbar(self, orient=VERTICAL, command=self.shield_listbox.yview)

        self.helmet_listbox = Listbox(self, selectmode=SINGLE, activestyle=NONE, height=20)
        self.helmet_listbox.bind("<<ListboxSelect>>", self.on_click_armor)
        self.helmet_scroll_bar = Scrollbar(self, orient=VERTICAL, command=self.helmet_listbox.yview)

        # labels for armor values
        self.ballistic_armor_label = ttk.Label(self, text="Ballistic Armor: ")
        self.impact_armor_label = ttk.Label(self, text="Impact Armor: ")
        self.quickness_penalty_label = ttk.Label(self, text="Quickness Penalty: ")
        self.combat_pool_penalty_label = ttk.Label(self, text="Combat Pool Penalty: ")

        self.ballistic_armor_val_label = ttk.Label(self, text="0")
        self.impact_armor_val_label = ttk.Label(self, text="0")
        self.quickness_penalty_val_label = ttk.Label(self, text="0")
        self.combat_pool_penalty_val_label = ttk.Label(self, text="0")

        # grids
        self.instruction_label.grid(column=0, row=0, columnspan=9999)

        ttk.Label(self, text="Body Armor").grid(column=0, row=2)
        self.armor_listbox.grid(column=0, row=1, sticky=(N, S))
        self.armor_scroll_bar.grid(column=1, row=1, sticky=(N, S))

        ttk.Label(self, text="Shield").grid(column=2, row=2)
        self.shield_listbox.grid(column=2, row=1, sticky=(N, S))
        self.shield_scroll_bar.grid(column=3, row=1, sticky=(N, S))

        ttk.Label(self, text="Helmet").grid(column=4, row=2)
        self.helmet_listbox.grid(column=4, row=1, sticky=(N, S))
        self.helmet_scroll_bar.grid(column=5, row=1, sticky=(N, S))

        self.ballistic_armor_label.grid(column=0, row=3)
        self.impact_armor_label.grid(column=0, row=4)
        self.quickness_penalty_label.grid(column=0, row=5)
        self.combat_pool_penalty_label.grid(column=0, row=6)

        self.ballistic_armor_val_label.grid(column=1, row=3)
        self.impact_armor_val_label.grid(column=1, row=4)
        self.quickness_penalty_val_label.grid(column=1, row=5)
        self.combat_pool_penalty_val_label.grid(column=1, row=6)

    def extract_val_from_armor(self, index, prop):
        """
        Gives you the value of the property from self.armor_list at the given index
        :param index: the index in armor_list to check
        :param prop: the property to check, ballistic or impact, could theoretically be anything though
        :return: value of the property
        """
        return self.armor_list[index].properties[prop]

    def on_click_armor(self, event):
        """
        Recalculates all armor values
        :param event: Does nothing
        :return: Nothing
        """

        # mark all equipped armors and unmark all unequipped armors
        size = self.armor_listbox.size()
        for i in range(0, size):
            self.armor_list[i].properties["equipped"] = self.armor_listbox.selection_includes(i)

        # get all equipped armors
        equipped_armors = list(filter(lambda x: x.properties["equipped"] is True, self.armor_list))
        self.statblock.calculate_armor_and_penalties(equipped_armors, None, None)

        self.ballistic_armor_val_label.configure(text=self.statblock.ballistic_armor)
        self.impact_armor_val_label.configure(text=self.statblock.impact_armor)
        self.quickness_penalty_val_label.configure(text=self.statblock.armor_quickness_penalty)
        self.combat_pool_penalty_val_label.configure(text=self.statblock.armor_combat_pool_penalty)

    def on_switch(self):
        self.armor_list.clear()
        self.armor_listbox.delete(0, END)

        # find all armor in inventory
        item: Gear
        for item in self.statblock.inventory:
            if "ballistic" in item.properties or "impact" in item.properties:
                if "armor_type" in item.properties:
                    if item.properties["armor_type"] == "shield":
                        pass
                    elif item.properties["armor_type"] == "helmet":
                        pass
                    else:
                        print(f"Invalid armor type {item.properties['armor_type']} for {item.properties['name']}.")
                        self.armor_list.append(item)
                else:
                    self.armor_list.append(item)

        # highlight anything equipped
        for armor in self.armor_list:
            self.armor_listbox.insert(END, armor.name)
            if armor.properties["equipped"]:
                self.armor_listbox.selection_set(END)

        self.on_click_armor(None)

    def load_character(self):
        self.on_switch()
