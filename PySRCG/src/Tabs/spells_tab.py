from copy import copy

from src.CharData.spell import Spell
from src.GenModes.finalized import Finalized
from src.Tabs.notebook_tab import NotebookTab
from src.adjustment import Adjustment
from src.utils import treeview_get, recursive_treeview_fill

from tkinter import *
from tkinter import ttk


class SpellsTab(NotebookTab):
    @property
    def library_selected(self) -> Spell:
        return treeview_get(self.magic_library, self.tree_library_dict)

    @property
    def list_selected_index(self) -> int:
        """index of the index of the selected item"""
        selection = self.magic_list.curselection()
        if len(selection) is 0:
            return None
        return selection[-1]

    def __init__(self, parent):
        super().__init__(parent)

        self.tree_library_dict = {}  # maps library terminal children iids

        # all learnable magic
        self.magic_library = ttk.Treeview(self, height=20, show="tree")
        self.magic_library_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.magic_library.yview)

        # description box
        self.desc_box = Text(self, width=40, state=DISABLED, bg='#d1d1d1')
        self.desc_box_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.desc_box.yview)

        # learned magic list
        self.magic_list = Listbox(self, width=40)
        self.magic_list_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.magic_list.yview)

        # learn, unlearn, plus, minus buttons
        self.learn_button = Button(self, text="Learn", command=self.on_learn_click)
        self.unlearn_button = Button(self, text="Unlearn", command=self.unlearn_spell)
        self.plus_button = Button(self, text="+", command=self.plus_spell)
        self.minus_button = Button(self, text="-", command=self.minus_spell)

        # bind events
        self.magic_library["yscrollcommand"] = self.magic_library_scroll.set
        self.desc_box["yscrollcommand"] = self.desc_box_scroll.set
        self.magic_list["yscrollcommand"] = self.magic_list_scroll.set

        # grids
        self.magic_library.grid(column=0, row=1, sticky=(N, S))
        self.magic_library_scroll.grid(column=1, row=1, sticky=(N, S))

        self.desc_box.grid(column=2, row=1, sticky=(N, S))
        self.desc_box_scroll.grid(column=3, row=1, sticky=(N, S))

        self.magic_list.grid(column=4, row=1, sticky=(N, S), columnspan=3)
        self.magic_list_scroll.grid(column=7, row=1, sticky=(N, S))

        self.learn_button.grid(column=0, row=2, sticky=N)
        self.unlearn_button.grid(column=4, row=2, sticky=N)
        self.plus_button.grid(column=5, row=2, sticky=N)
        self.minus_button.grid(column=6, row=2, sticky=N)

        def magic_tab_recurse_check(val):
            return "drain" not in val.keys()

        def magic_tab_recurse_end_callback(key, val, iid):
            # key is a string
            # val is a dict from a json
            self.tree_library_dict[iid] = Spell(name=key, **val, force=0)

        recursive_treeview_fill(self.parent.game_data["Spells"], "", self.magic_library,
                                magic_tab_recurse_check, magic_tab_recurse_end_callback)

    def on_learn_click(self):
        if self.library_selected is not None:
            magic_total = 0

            # check to make sure it's not already there
            for val in self.statblock.spells:
                if val.name == self.library_selected.name:
                    print("Already have that learned!")
                    return

                magic_total += val.force

            if self.statblock.gen_mode.point_purchase_allowed(magic_total, "magic"):
                # make a spell object, then add to the player's magic list

                new_spell = copy(self.library_selected)
                new_spell.force += 1
                self.add_spell_item(new_spell)

                # do this if we're finalized
                if type(self.gen_mode) == Finalized:
                    def undo():
                        return  # do nothing, will be handled in unlearn_spell

                    adjustment = Adjustment(1, "add_spell_" + new_spell.name, undo, "Add new spell")
                    self.gen_mode.add_adjustment(adjustment)

                self.calculate_total()

        else:
            print("Can't learn that!")

    def unlearn_spell(self):
        # don't do anything if nothing is selected
        if len(self.magic_list.curselection()) is 0:
            return

        selected_spell: Spell = self.statblock.spells[self.list_selected_index]

        if type(self.gen_mode) == Finalized:
            if self.gen_mode.remove_by_adjustment_type(selected_spell, "add_spell_", "increase_spell_"):
                self.gen_mode.undo("add_spell_" + selected_spell.name)
                self.remove_spell_item(self.list_selected_index)
            else:
                print("Can't remove that!")

        else:
            self.remove_spell_item(self.list_selected_index)
        self.calculate_total()

    def add_spell_item(self, item: Spell):
        # add to listbox
        self.statblock.spells.append(item)
        self.magic_list.insert(END, item.force_and_name())

    def remove_spell_item(self, index):
        del self.statblock.spells[index]
        self.magic_list.delete(index)

    def plus_spell(self):
        # set the check value based on the generation mode
        check_val = 1 if type(self.gen_mode) == Finalized else self.get_total()

        if self.list_selected_index is not None and \
                self.statblock.gen_mode.point_purchase_allowed(check_val, "magic"):
            selected_spell = self.statblock.spells[self.list_selected_index]
            max_force = 99 if type(self.gen_mode) == Finalized else 6

            if selected_spell.force < max_force:
                selected_spell.force += 1

                # update UI by removing the old one and inserting a new one at the same index
                i = self.list_selected_index
                self.magic_list.delete(i)
                self.magic_list.insert(i, selected_spell.force_and_name())
                self.magic_list.selection_set(i)

                if type(self.gen_mode) == Finalized:
                    # undo function
                    def undo():
                        selected_spell.force -= 1

                    adjustment = Adjustment(1, "increase_spell_" + selected_spell.name, undo)
                    self.gen_mode.add_adjustment(adjustment)

                self.calculate_total()

    def minus_spell(self):
        if self.list_selected_index is not None:
            selected_spell = self.statblock.spells[self.list_selected_index]

            if selected_spell.force > 1:
                if type(self.gen_mode) is Finalized:
                    undo_type = "increase_spell_" + selected_spell.name
                    self.statblock.gen_mode.undo(undo_type)
                else:
                    selected_spell.force -= 1

                # update UI by removing the old one and inserting a new one at the same index
                i = self.list_selected_index
                self.magic_list.delete(i)
                self.magic_list.insert(i, selected_spell.force_and_name())
                self.magic_list.selection_set(i)

                self.calculate_total()

    def get_total(self):
        total = 0

        for spell in self.statblock.spells:
            total += spell.force

        return total

    def calculate_total(self):
        """Totals all spell points and updates the top karma bar."""
        self.statblock.gen_mode.update_total(self.get_total(), "magic")

    @property
    def char_tradition(self):
        return self.statblock.magic_tradition

    def on_tradition_change(self):
        return

    def load_character(self):
        # clear everything
        self.magic_list.delete(0, END)

        # add stuff to the list
        for spell in self.statblock.spells:
            self.magic_list.insert(END, spell.force_and_name())

        self.on_switch()

    def on_switch(self):

        self.calculate_total()