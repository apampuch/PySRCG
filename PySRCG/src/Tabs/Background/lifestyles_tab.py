from abc import ABC
from tkinter import *
from tkinter import ttk

from src.CharData.lifestyle import *
from src.Tabs.notebook_tab import NotebookTab


class LifestylesTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)

        # frame for existing lifestyles
        self.list_frame = LabelFrame(self, text="Lifestyles")

        # listbox for lifestyles + scrollbar
        self.list_and_scrollbar = Frame(self.list_frame)
        self.lifestyles_listbox = Listbox(self.list_and_scrollbar, selectmode=BROWSE, exportselection=False)
        self.lifestyles_listbox_scroll = ttk.Scrollbar(self.list_and_scrollbar, orient=VERTICAL,
                                                       command=self.lifestyles_listbox.yview)
        self.lifestyles_listbox["yscrollcommand"] = self.lifestyles_listbox_scroll.set
        self.lifestyles_listbox.bind("<<ListboxSelect>>", self.on_select_listbox)

        # buttons for add/delete lifestyle
        self.lifestyles_buttons = Frame(self.list_frame)
        self.add_button = Button(self.lifestyles_buttons, text="New Lifestyle", command=self.new_lifestyle)
        self.remove_button = Button(self.lifestyles_buttons, text="Delete Lifestyle", command=self.delete_lifestyle)

        self.lifestyle_data_frame = Frame(self)
        # radio buttons for simple and advanced lifestyles
        self.simple_advanced_frame = LabelFrame(self.lifestyle_data_frame, text="Lifestyle Type")
        self.setup_type = StringVar()
        self.setup_type.set("Simple")
        self.simple_setup = Radiobutton(self.simple_advanced_frame,
                                        text="Simple",
                                        variable=self.setup_type,
                                        value="Simple",
                                        command=lambda: self.on_simple_selected())
        self.advanced_setup = Radiobutton(self.simple_advanced_frame,
                                          text="Advanced",
                                          variable=self.setup_type,
                                          value="Advanced", width=20,
                                          command=lambda: self.on_advanced_selected())

        # simple lifestyle info
        self.simple_info = SimpleLifestyleInfo(self.lifestyle_data_frame)
        self.advanced_info = AdvancedLifestyleInfo(self.lifestyle_data_frame)

        self.general_info_frame = Frame(self)
        # name
        self.name_label = Label(self.general_info_frame, text="Name")
        self.name_var = StringVar()
        self.name_var.trace("w", lambda x, y, z: self.on_name_updated())
        self.name_entry = Entry(self.general_info_frame, textvariable=self.name_var, width=40)

        # residence
        self.residence_label = Label(self.general_info_frame, text="Residence")
        self.residence_entry = Text(self.general_info_frame, width=30, height=5)
        self.residence_entry.bind("<<Modified>>",
                                  lambda x: self.on_text_updated(self.residence_entry))

        # month/year
        self.month_year_label = Label(self.general_info_frame, text="Month/Year")
        self.month_var = IntVar()
        self.month_spin = Spinbox(self.general_info_frame, from_=1, to=12, wrap=True, width=2,
                                  textvariable=self.month_var)
        self.month_var.trace("w", lambda x, y, z: self.on_month_updated())
        self.year_var = IntVar()
        self.year_var.set(2050)
        self.year_var.trace("w", lambda x, y, z: self.on_year_updated())
        self.year_spin = Spinbox(self.general_info_frame, from_=0, to=9999, textvariable=self.year_var, width=4)

        # ltg
        self.LTG_label = Label(self.general_info_frame, text="LTG")
        self.LTG_var = StringVar()
        self.LTG_var.trace("w", lambda x, y, z: self.on_LTG_updated())
        self.LTG_entry = Entry(self.general_info_frame, textvariable=self.LTG_var, width=40)

        # description
        self.description_label = Label(self.general_info_frame, text="Description")
        self.description_entry = Text(self.general_info_frame, width=30, height=5)
        self.description_entry.bind("<<Modified>>",
                                    lambda x: self.on_text_updated(self.description_entry))

        # notes
        self.notes_label = Label(self.general_info_frame, text="Notes")
        self.notes_entry = Text(self.general_info_frame, width=30, height=5)
        self.notes_entry.bind("<<Modified>>",
                              lambda x: self.on_text_updated(self.notes_entry))

        # grids
        self.list_frame.grid(column=0, row=0, sticky=N)
        self.simple_advanced_frame.grid(column=1, row=0, sticky=N)

        self.lifestyle_data_frame.grid(column=1, row=0, sticky=N)
        self.general_info_frame.grid(column=2, row=0)

        self.name_label.grid(column=0, row=0)
        self.name_entry.grid(column=1, row=0, columnspan=2, sticky=W)

        self.residence_label.grid(column=0, row=1)
        self.residence_entry.grid(column=1, row=1, columnspan=2, sticky=W)

        self.month_year_label.grid(column=0, row=2)
        self.month_spin.grid(column=1, row=2)
        self.year_spin.grid(column=2, row=2)

        self.LTG_label.grid(column=0, row=3)
        self.LTG_entry.grid(column=1, row=3, columnspan=2, sticky=W)

        self.description_label.grid(column=0, row=4)
        self.description_entry.grid(column=1, row=4, columnspan=2, sticky=W)

        self.notes_label.grid(column=0, row=5)
        self.notes_entry.grid(column=1, row=5, columnspan=2, sticky=W)

        # self.simple_info.grid(column=1, row=1, sticky=EW)

        self.list_and_scrollbar.grid(column=0, row=0)
        self.lifestyles_buttons.grid(column=0, row=1)

        self.lifestyles_listbox.grid(column=0, row=0)
        self.lifestyles_listbox_scroll.grid(column=1, row=0, sticky=NS)
        self.add_button.grid(column=0, row=0)
        self.remove_button.grid(column=1, row=0)

        self.simple_setup.grid(column=0, row=0)
        self.advanced_setup.grid(column=1, row=0)

    def new_lifestyle(self):
        # make the lifestyle, add to character, select it
        new_lifestyle = SimpleLifestyle(
            name="New Lifestyle",
            residence="",
            permanent=False,
            month=1,
            year=2050,
            LTG="",
            description="",
            notes="",
            tier=0)
        self.character.lifestyles.append(new_lifestyle)
        self.lifestyles_listbox.insert(END, new_lifestyle.name)
        self.lifestyles_listbox.selection_clear(0, END)
        self.lifestyles_listbox.selection_set(END)

        self.show_simple_info()
        self.name_var.set("New Lifestyle")
        self.simple_info.tier_selector.set("Street (Free)")

        self.on_select_listbox(None)

    def delete_lifestyle(self):
        if len(self.character.lifestyles) > 0:
            index = self.lifestyles_listbox.curselection()[0]
            del self.character.lifestyles[index]
            self.lifestyles_listbox.delete(index)

            if len(self.character.lifestyles) == 0:
                self.simple_info.grid_forget()
                self.advanced_info.grid_forget()
            else:
                new_index = min(index, len(self.character.lifestyles) - 1)
                self.lifestyles_listbox.selection_clear(0, END)
                self.lifestyles_listbox.selection_set(new_index)

                # change the grid based on if the next one is simple or advanced
                self.on_select_listbox(None)

    def on_simple_selected(self):
        if len(self.character.lifestyles) > 0:
            index = self.lifestyles_listbox.curselection()[0]
            selected = self.character.lifestyles[index]

            # switch to simple type
            if type(selected) is AdvancedLifestyle:
                self.character.lifestyles[index] = SimpleLifestyle.fromAdvanced(selected)
                self.show_simple_info()

            self.on_select_listbox(None)

    def on_advanced_selected(self):
        if len(self.character.lifestyles) > 0:
            index = self.lifestyles_listbox.curselection()[0]
            selected = self.character.lifestyles[index]

            # switch to advanced type
            if type(selected) is SimpleLifestyle:
                self.character.lifestyles[index] = AdvancedLifestyle.fromSimple(selected)
                self.show_advanced_info()

            self.on_select_listbox(None)

    def show_simple_info(self):
        self.advanced_info.grid_forget()
        self.simple_info.grid(column=1, row=1, sticky=EW)

    def show_advanced_info(self):
        self.simple_info.grid_forget()
        self.advanced_info.grid(column=1, row=1, sticky=EW)

    # noinspection PyUnusedLocal
    def on_select_listbox(self, dummyvar):
        # load basic data
        lifestyle = self.character.lifestyles[self.lifestyles_listbox.curselection()[0]]
        self.name_var.set(lifestyle.name)
        self.residence_entry.delete(0.0, END)
        self.residence_entry.insert(END, lifestyle.residence)
        self.month_var.set(lifestyle.month)
        self.year_var.set(lifestyle.year)
        self.LTG_var.set(lifestyle.LTG)
        self.description_entry.delete(0.0, END)
        self.description_entry.insert(END, lifestyle.description)
        self.notes_entry.delete(0.0, END)
        self.notes_entry.insert(END, lifestyle.notes)

        # load cost data
        lifestyle_type = type(lifestyle)
        self.setup_type.set(lifestyle_type.type)

        # set combobox values based on tiers
        if lifestyle_type is SimpleLifestyle:
            lifestyle: SimpleLifestyle
            self.simple_info.selected_tier.set(SimpleLifestyleInfo.tiers[lifestyle.tier])
        elif lifestyle_type is AdvancedLifestyle:
            lifestyle: AdvancedLifestyle
            self.advanced_info.selected_area.set(AdvancedLifestyleInfo.area_tiers[lifestyle.area])
            self.advanced_info.selected_comforts.set(AdvancedLifestyleInfo.other_tiers[lifestyle.comforts])
            self.advanced_info.selected_entertainment.set(AdvancedLifestyleInfo.other_tiers[lifestyle.entertainment])
            self.advanced_info.selected_furnishings.set(AdvancedLifestyleInfo.other_tiers[lifestyle.furnishings])
            self.advanced_info.selected_security.set(AdvancedLifestyleInfo.other_tiers[lifestyle.security])
            self.advanced_info.selected_space.set(AdvancedLifestyleInfo.other_tiers[lifestyle.space])
        else:
            raise TypeError("Selected lifestyle is invalid type!")

    def on_month_updated(self):
        sel = self.lifestyles_listbox.curselection()
        if len(self.character.lifestyles) > 0 and len(sel) > 0:
            index = sel[0]
            self.character.lifestyles[index].month = self.month_var.get()

    def on_year_updated(self):
        # suppress an error where this is called when the character doesn't exist
        if self.character is None:
            return

        sel = self.lifestyles_listbox.curselection()
        if len(self.character.lifestyles) > 0 and len(sel) > 0:
            index = sel[0]
            self.character.lifestyles[index].year = self.year_var.get()

    def on_text_updated(self, text_entry):
        get_dict = {
            self.residence_entry: "residence",
            self.description_entry: "description",
            self.notes_entry: "notes"
        }

        sel = self.lifestyles_listbox.curselection()
        if len(self.character.lifestyles) > 0 and len(sel) > 0 and text_entry in get_dict:
            index = sel[0]
            prop = get_dict[text_entry]
            setattr(self.character.lifestyles[index], prop, text_entry.get(0.0, END))

        text_entry.edit_modified(False)

    def on_name_updated(self):
        sel = self.lifestyles_listbox.curselection()
        if len(self.character.lifestyles) > 0 and len(sel) > 0:
            index = sel[0]
            self.lifestyles_listbox.delete(index)
            self.lifestyles_listbox.insert(index, self.name_var.get())
            self.lifestyles_listbox.selection_set(index)
            self.character.lifestyles[index].name = self.name_var.get()

    # noinspection PyPep8Naming
    def on_LTG_updated(self):
        sel = self.lifestyles_listbox.curselection()
        if len(self.character.lifestyles) > 0 and len(sel) > 0:
            index = sel[0]
            self.character.lifestyles[index].LTG = self.LTG_var.get()

    def on_combobox_changed(self, box_var, field):
        sel = self.lifestyles_listbox.curselection()
        if len(self.character.lifestyles) > 0 and len(sel) > 0:
            index = sel[0]

            # get integer from string
            # this is less retarded than using a dict for reasons
            if field == "tier":
                val = SimpleLifestyleInfo.tiers.index(box_var.get())
            elif field == "area":
                val = AdvancedLifestyleInfo.area_tiers.index(box_var.get())
            else:
                val = AdvancedLifestyleInfo.other_tiers.index(box_var.get())

            setattr(self.character.lifestyles[index], field, val)

    def reload_data(self):
        pass

    def on_switch(self):
        pass

    def load_character(self):
        pass


class SimpleLifestyleInfo(LabelFrame):
    tiers = ("Street (Free)", "Squatter (¥100)", "Low (¥1000)", "Middle (¥5000)", "High (¥10000)", "Luxury (¥100000)")

    def __init__(self, parent):
        super().__init__(parent, text="Cost")
        self.parent = parent

        self.selected_tier = StringVar()
        self.selected_tier.trace("w", lambda x, y, z: parent.master.on_combobox_changed(self.selected_tier, "tier"))
        self.tier_selector = ttk.Combobox(self, textvariable=self.selected_tier, state="readonly",
                                          values=SimpleLifestyleInfo.tiers)

        self.tier_selector.grid(column=0, row=0, padx=5, pady=5)


class AdvancedLifestyleInfo(LabelFrame):
    area_tiers = ("Z—Street-equivalent (-1 points)", "E—Street-equivalent (0 points)",
                  "D—Squatter-equivalent (1 points)", "C—Low-equivalent (2 points)",
                  "B—Middle-equivalent (3 points)", "A—High-equivalent (4 points)",
                  "AA—Luxury-equivalent (5 points)", "AAA—Luxury-equivalent (6 points)")

    other_tiers = ("Street-equivalent (0 points)", "Squatter-equivalent (1 points)", "Low-equivalent (2 points)",
                   "Middle-equivalent (3 points)", "High-equivalent (4 points)", "Luxury-equivalent (5 points)")

    def __init__(self, parent):
        super().__init__(parent, text="Advanced")
        self.parent = parent

        self.selected_area = StringVar()
        self.selected_area.trace("w", lambda x, y, z: parent.master.on_combobox_changed(self.selected_area, "area"))
        self.area_selector = ttk.Combobox(self, textvariable=self.selected_area, state="readonly",
                                          values=AdvancedLifestyleInfo.area_tiers)

        self.selected_comforts = StringVar()
        self.selected_comforts.trace("w", lambda x, y, z: parent.master.on_combobox_changed(
            self.selected_comforts, "comforts"))
        self.comforts_selector = ttk.Combobox(self, textvariable=self.selected_comforts, state="readonly",
                                              values=AdvancedLifestyleInfo.other_tiers)

        self.selected_entertainment = StringVar()
        self.selected_entertainment.trace("w", lambda x, y, z: parent.master.on_combobox_changed(
            self.selected_entertainment, "entertainment"))
        self.entertainment_selector = ttk.Combobox(self, textvariable=self.selected_entertainment, state="readonly",
                                                   values=AdvancedLifestyleInfo.other_tiers)

        self.selected_furnishings = StringVar()
        self.selected_furnishings.trace("w", lambda x, y, z: parent.master.on_combobox_changed(
            self.selected_furnishings, "furnishings"))
        self.furnishings_selector = ttk.Combobox(self, textvariable=self.selected_furnishings, state="readonly",
                                                 values=AdvancedLifestyleInfo.other_tiers)

        self.selected_security = StringVar()
        self.selected_security.trace("w", lambda x, y, z: parent.master.on_combobox_changed(
            self.selected_security, "security"))
        self.security_selector = ttk.Combobox(self, textvariable=self.selected_security, state="readonly",
                                              values=AdvancedLifestyleInfo.other_tiers)

        self.selected_space = StringVar()
        self.selected_space.trace("w", lambda x, y, z: parent.master.on_combobox_changed(
            self.selected_space, "space"))
        self.space_selector = ttk.Combobox(self, textvariable=self.selected_space, state="readonly",
                                           values=AdvancedLifestyleInfo.other_tiers)

        Label(self, text="Area").grid(column=0, row=0, padx=5, pady=5)
        Label(self, text="Comforts").grid(column=0, row=1, padx=5, pady=5)
        Label(self, text="Entertainment").grid(column=0, row=2, padx=5, pady=5)
        Label(self, text="Furnishings").grid(column=0, row=3, padx=5, pady=5)
        Label(self, text="Security").grid(column=0, row=4, padx=5, pady=5)
        Label(self, text="Space").grid(column=0, row=5, padx=5, pady=5)

        self.area_selector.grid(column=1, row=0, padx=5, pady=5)
        self.comforts_selector.grid(column=1, row=1, padx=5, pady=5)
        self.entertainment_selector.grid(column=1, row=2, padx=5, pady=5)
        self.furnishings_selector.grid(column=1, row=3, padx=5, pady=5)
        self.security_selector.grid(column=1, row=4, padx=5, pady=5)
        self.space_selector.grid(column=1, row=5, padx=5, pady=5)
