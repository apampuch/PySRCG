from abc import ABC
from tkinter import *
from tkinter import ttk
from typing import Any

from src.CharData.contact import Contact
from src.GenModes.finalized import Finalized
from src.Tabs.notebook_tab import NotebookTab


class ContactsTab(NotebookTab, ABC):
    affiliation_prices = [5000, 10000, 200000]

    def selected(self) -> Any | None:
        try:
            selected_index = self.contacts_listbox.curselection()[0]
            selected: Contact
            return self.character.contacts[selected_index]
        except IndexError:
            return None

    def __init__(self, parent):
        super().__init__(parent)

        self.list_frame = LabelFrame(self, text="Contacts List")
        self.contacts_listbox = Listbox(self.list_frame, selectmode=BROWSE, exportselection=False)
        self.contacts_listbox.bind("<<ListboxSelect>>", self.on_select_listbox)

        self.add_button = Button(self.list_frame, text="New Contact", command=self.on_add_click)
        self.remove_button = Button(self.list_frame, text="Remove", command=self.on_remove_click)

        self.contact_frame = Frame(self)

        self.name_label = Label(self.contact_frame, text="Name")
        self.name_var = StringVar()
        self.name_var.trace("w", lambda x, y, z: self.on_name_updated())
        self.name_entry = Entry(self.contact_frame, textvariable=self.name_var, state=DISABLED)

        self.archetype_label = Label(self.contact_frame, text="Archetype")
        self.archetype_var = StringVar()
        self.archetype_var.trace("w", lambda x, y, z: self.on_archetype_updated())
        self.archetype_entry = Entry(self.contact_frame, textvariable=self.archetype_var, state=DISABLED)

        self.location_label = Label(self.contact_frame, text="Location")
        self.location_var = StringVar()
        self.location_var.trace("w", lambda x, y, z: self.on_location_updated())
        self.location_entry = Entry(self.contact_frame, textvariable=self.location_var, state=DISABLED)

        self.LTG_label = Label(self.contact_frame, text="LTG")
        self.LTG_var = StringVar()
        self.LTG_var.trace("w", lambda x, y, z: self.on_LTG_updated())
        self.LTG_entry = Entry(self.contact_frame, textvariable=self.LTG_var, state=DISABLED)

        self.affiliation_label = Label(self.contact_frame, text="Affiliation")
        self.affiliation_var = IntVar()
        self.affiliation_var.trace("w", lambda x, y, z: self.on_affiliation_updated())
        self.affiliation_spinbox = Spinbox(self.contact_frame, textvariable=self.affiliation_var, from_=1, to=3,
                                           state=DISABLED, width=2, readonlybackground="#ffffff")

        self.texts_frame = Frame(self.contact_frame)

        self.description_label = Label(self.texts_frame, text="Description")
        self.description_text = Text(self.texts_frame, width=30, height=5)
        self.description_text.bind("<<Modified>>", lambda x: self.on_description_updated())
        self.description_text.config(state=DISABLED, bg="#f0f0f0")

        self.history_label = Label(self.texts_frame, text="History")
        self.history_text = Text(self.texts_frame, width=30, height=5, state=DISABLED)
        self.history_text.bind("<<Modified>>", lambda x: self.on_history_updated())
        self.history_text.config(state=DISABLED, bg="#f0f0f0")

        # grids
        self.list_frame.grid(column=0, row=0, sticky=N, padx=5, pady=5)
        self.contact_frame.grid(column=1, row=0, sticky=N, padx=5, pady=5)

        self.contacts_listbox.grid(column=0, row=0, columnspan=2)
        self.add_button.grid(column=0, row=1)
        self.remove_button.grid(column=1, row=1)

        self.name_label.grid(column=0, row=0)
        self.name_entry.grid(column=1, row=0, sticky=W)

        self.archetype_label.grid(column=0, row=1)
        self.archetype_entry.grid(column=1, row=1, sticky=W)

        self.location_label.grid(column=0, row=2)
        self.location_entry.grid(column=1, row=2, sticky=W)

        self.LTG_label.grid(column=0, row=3)
        self.LTG_entry.grid(column=1, row=3, sticky=W)

        self.affiliation_label.grid(column=0, row=4)
        self.affiliation_spinbox.grid(column=1, row=4, sticky=W)

        self.texts_frame.grid(column=0, row=5, columnspan=2)

        self.description_label.grid(column=0, row=0)
        self.description_text.grid(column=0, row=1)
        self.history_label.grid(column=0, row=2)
        self.history_text.grid(column=0, row=3)

    def on_select_listbox(self, dummyvar):
        if len(self.contacts_listbox.curselection()) > 0:
            self.name_entry.config(state=NORMAL)
            self.archetype_entry.config(state=NORMAL)
            self.location_entry.config(state=NORMAL)
            self.LTG_entry.config(state=NORMAL)
            self.affiliation_spinbox.config(state="readonly")
            self.description_text.config(state=NORMAL, bg="#ffffff")
            self.history_text.config(state=NORMAL, bg="#ffffff")

            # set vars
            self.name_var.set(self.selected().name)
            self.archetype_var.set(self.selected().archetype)
            self.location_var.set(self.selected().location)
            self.LTG_var.set(self.selected().LTG)
            self.affiliation_var.set(self.selected().affiliation)
            self.description_text.delete(0.0, END)
            self.description_text.insert(0.0, self.selected().description)
            self.history_text.delete(0.0, END)
            self.history_text.insert(0.0, self.selected().history)
        else:
            # clear vars
            self.name_var.set("")
            self.archetype_var.set("")
            self.location_var.set("")
            self.LTG_var.set("")
            self.affiliation_var.set(0)
            self.description_text.delete(0.0, END)
            self.history_text.delete(0.0, END)

            # disable
            self.name_entry.config(state=DISABLED)
            self.archetype_entry.config(state=DISABLED)
            self.location_entry.config(state=DISABLED)
            self.LTG_entry.config(state=DISABLED)
            self.affiliation_spinbox.config(state=DISABLED)
            self.description_text.config(state=DISABLED, bg="#f0f0f0")
            self.history_text.config(state=DISABLED, bg="#f0f0f0")

    def on_add_click(self):
        # check if we have enough money if we're not already finalized
        if type(self.character.statblock.gen_mode) is not Finalized:
            if not self.character.statblock.pay_cash(5000):
                print("Not enough cash!")

        # add to character
        new_contact = Contact("New Contact", "", "", 1, "", "", "")
        self.character.contacts.append(new_contact)
        self.contacts_listbox.insert(END, new_contact.name)
        self.contacts_listbox.selection_clear(0, END)
        self.contacts_listbox.selection_set(END)
        self.on_select_listbox(None)

    def on_remove_click(self):
        selected_index = self.contacts_listbox.curselection()[0]

        # refund based on affiliation if we're not finalized
        if type(self.character.statblock.gen_mode) is not Finalized:
            refund = ContactsTab.affiliation_prices[self.character.contacts[selected_index].affiliation - 1]
            self.character.statblock.add_cash(refund)

        self.contacts_listbox.delete(selected_index)
        del self.character.contacts[selected_index]

        # fix selection
        self.contacts_listbox.selection_clear(0, END)
        if len(self.character.contacts) == 0:
            pass
        elif selected_index == len(self.character.contacts):
            self.contacts_listbox.selection_set(END)
        else:
            self.contacts_listbox.selection_set(selected_index)

        self.on_select_listbox(None)

    def on_name_updated(self):
        if self.selected() is not None:
            self.selected().name = self.name_var.get()

            # update listbox text
            index = self.contacts_listbox.curselection()[0]
            self.contacts_listbox.delete(index)
            self.contacts_listbox.insert(index, self.name_var.get())
            self.contacts_listbox.selection_set(index)
            self.character.contacts[index].name = self.name_var.get()

    def on_archetype_updated(self):
        if self.selected() is not None:
            self.selected().archetype = self.archetype_var.get()

    def on_location_updated(self):
        if self.selected() is not None:
            self.selected().location = self.location_var.get()

    def on_LTG_updated(self):
        if self.selected() is not None:
            self.selected().LTG = self.LTG_var.get()

    def on_affiliation_updated(self):
        if self.selected() is not None:
            self.selected().affiliation = self.affiliation_var.get()

    def on_description_updated(self):
        if self.selected() is not None:
            self.selected().description = self.description_text.get(0.0, END)
            self.description_text.edit_modified(False)

    def on_history_updated(self):
        if self.selected() is not None:
            self.selected().history = self.history_text.get(0.0, END)
            self.history_text.edit_modified(False)

    def reload_data(self):
        pass

    def on_switch(self):
        pass

    def load_character(self):
        self.contacts_listbox.delete(0, END)
        for contact in self.character.contacts:
            self.contacts_listbox.insert(END, contact.name)

        # fix selection
        self.contacts_listbox.selection_clear(0, END)
        self.on_select_listbox(None)
