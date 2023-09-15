from abc import ABC

from src.Tabs.notebook_tab import NotebookTab
from tkinter import *
from tkinter import ttk


class PersonalInfoTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "PersonalInfoTab")

        # names frame
        self.names_frame = LabelFrame(self, text="Names")
        # name box
        ttk.Label(self.names_frame, text="Name").grid(column=0, row=0, padx=5, pady=3)
        ttk.Label(self.names_frame, text="Real Name").grid(column=0, row=1, padx=5, pady=3)
        ttk.Label(self.names_frame, text="Street Names").grid(column=0, row=2, padx=5, pady=3)
        self.name_box = Entry(self.names_frame, width=20)
        self.real_name_box = Entry(self.names_frame, width=20)
        self.street_names_box = Text(self.names_frame, width=20, height=5)
        self.street_names_box.bind("<<Modified>>",
                                   lambda x: self.set_char_string(self.character.street_names, self.street_names_box))

        # physical appearance frame
        self.physical_appearance_frame = LabelFrame(self, text="Physical Appearance")
        # sex box
        ttk.Label(self.physical_appearance_frame, text="Sex").grid(column=0, row=0, padx=5, pady=5)
        self.male_button = Radiobutton(self.physical_appearance_frame, text="M", value="Male")
        self.female_button = Radiobutton(self.physical_appearance_frame, text="F", value="Female")
        self.male_button.select()  # select male as default so we have one
        # height and weight
        ttk.Label(self.physical_appearance_frame, text="Height").grid(column=0, row=1, padx=5, pady=5)
        self.height_box = Entry(self.physical_appearance_frame, width=5)
        ttk.Label(self.physical_appearance_frame, text="kg").grid(column=2, row=1, padx=5, pady=5)
        ttk.Label(self.physical_appearance_frame, text="Weight").grid(column=0, row=2, padx=5, pady=5)
        self.weight_box = Entry(self.physical_appearance_frame, width=5)
        ttk.Label(self.physical_appearance_frame, text="cm").grid(column=2, row=2, padx=5, pady=5)
        # hair
        ttk.Label(self.physical_appearance_frame, text="Hair").grid(column=0, row=3, padx=5, pady=5)
        self.hair_box = Entry(self.physical_appearance_frame)
        # eyes
        ttk.Label(self.physical_appearance_frame, text="Eyes").grid(column=0, row=4, padx=5, pady=5)
        self.eyes_box = Entry(self.physical_appearance_frame)
        # appearance
        ttk.Label(self.physical_appearance_frame, text="Appearance").grid(column=0, row=5, padx=5, pady=5)
        self.appearance_box = Text(self.physical_appearance_frame, width=20, height=4)
        self.appearance_box.bind("<<Modified>>",
                                 lambda x: self.set_char_string(self.character.appearance, self.appearance_box))
        # archetype
        ttk.Label(self.physical_appearance_frame, text="Archetype").grid(column=0, row=6, padx=5, pady=5)
        self.archetype_box = Entry(self.physical_appearance_frame)

        # birth
        self.birth_frame = LabelFrame(self, text="Birth Info")
        ttk.Label(self.birth_frame, text="Birth Date").grid(column=0, row=0)
        self.birthdate_entry = Entry(self.birth_frame)
        ttk.Label(self.birth_frame, text="Birth Place").grid(column=0, row=1)
        self.birthplace_entry = Entry(self.birth_frame)
        ttk.Label(self.birth_frame, text="Birth Notes").grid(column=0, row=2)
        self.birth_notes = Text(self.birth_frame, width=20, height=4)
        self.birth_notes.bind("<<Modified>>",
                              lambda x: self.set_char_string(self.character.birth_notes, self.birth_notes))

        # notes
        self.notes_frame = LabelFrame(self, text="Notes")
        self.notes_entry = Text(self.notes_frame, width=30, height=15)
        self.notes_entry.bind("<<Modified>>",
                              lambda x: self.set_char_string(self.character.notes, self.notes_entry))
        ttk.Label(self.notes_frame, text="Creator").grid(column=0, row=1)
        self.creator_entry = Entry(self.notes_frame)

        self.names_frame.grid(column=0, row=0, padx=5, pady=5, sticky=EW)
        self.physical_appearance_frame.grid(column=0, row=1, padx=5, pady=5, sticky=EW)
        self.birth_frame.grid(column=1, row=0, padx=5, pady=5, sticky=NSEW)
        self.notes_frame.grid(column=1, row=1, padx=5, pady=5, sticky=NSEW)

        self.name_box.grid(column=1, row=0, columnspan=2, padx=5, pady=3)
        self.real_name_box.grid(column=1, row=1, columnspan=2, padx=5, pady=3)
        self.street_names_box.grid(column=1, row=2, columnspan=2, padx=5, pady=3)

        self.male_button.grid(column=1, row=0)
        self.female_button.grid(column=2, row=0)
        self.height_box.grid(column=1, row=1)
        self.weight_box.grid(column=1, row=2)
        self.hair_box.grid(column=1, row=3, columnspan=2)
        self.eyes_box.grid(column=1, row=4, columnspan=2)
        self.appearance_box.grid(column=1, row=5, columnspan=2)
        self.archetype_box.grid(column=1, row=6, columnspan=2)

        self.birthdate_entry.grid(column=1, row=0, padx=5, pady=3)
        self.birthplace_entry.grid(column=1, row=1, padx=5, pady=3)
        self.birth_notes.grid(column=1, row=2, padx=5, pady=3)

        self.notes_entry.grid(column=0, row=0, padx=5, pady=3, columnspan=2)
        self.creator_entry.grid(column=1, row=1, padx=5, pady=3, columnspan=2)

    @staticmethod
    def set_char_string(char_var, text_widget: Text):
        char_var.set(text_widget.get(0.0, END))
        text_widget.edit_modified(False)

    def on_switch(self):
        pass

    def load_character(self):
        self.name_box.config(textvariable=self.character.name)
        self.real_name_box.config(textvariable=self.character.real_name)
        self.street_names_box.delete(1.0, END)
        self.street_names_box.insert(END, self.character.street_names.get())

        self.male_button.config(variable=self.character.sex)
        self.female_button.config(variable=self.character.sex)
        self.height_box.config(textvariable=self.character.height)
        self.weight_box.config(textvariable=self.character.weight)
        self.hair_box.config(textvariable=self.character.hair)
        self.eyes_box.config(textvariable=self.character.eyes)
        self.appearance_box.delete(1.0, END)
        self.appearance_box.insert(END, self.character.appearance.get())
        self.archetype_box.config(textvariable=self.character.archetype)

        self.birthdate_entry.config(textvariable=self.character.birthdate)
        self.birthplace_entry.config(textvariable=self.character.birthplace)
        self.birth_notes.delete(1.0, END)
        self.birth_notes.insert(END, self.character.birth_notes.get())

        self.notes_entry.delete(1.0, END)
        self.notes_entry.insert(END, self.character.notes.get())
        self.creator_entry.config(textvariable=self.character.creator)

        if self.character.sex.get() == "Male":
            self.male_button.select()
        elif self.character.sex.get() == "Female":
            self.female_button.select()
        else:
            raise ValueError("Gender {} not found.".format(self.character.sex.get()))
