from abc import ABC
from tkinter import *
from tkinter import ttk

from src.Tabs.notebook_tab import NotebookTab


class BankingTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)

        """
        This is a listbox for currencies. When a currency is clicked, the other boxes will auto-populate.
        Editing them will edit the currency.
        Pressing the "new currency" button will populate this box with a new currency that can be edited.
        Each item in the listbox maps to one Currency object in self.statblock.currencies
        The listbox will always be populated with a single "Miscellaneous Cash" object that does not map
        to a Currency, it instead represenes the misc_cash variable in the statblock.
        """
        self.treasury_frame = LabelFrame(self, text="Treasury", padx=5, pady=5)
        self.all_currencies = Listbox(self.treasury_frame, width=50, selectmode=SINGLE)

        self.data_entry_frame = LabelFrame(self, text="Selected Item", padx=5, pady=5)
        # name entry
        name_label = Label(self.data_entry_frame, text="Name")
        self.name_entry = Entry(self.data_entry_frame, width=30)

        # currency type combobox
        currency_label = Label(self.data_entry_frame, text="Currency")
        currency_options = ("Credstick", "Currency", "Scrip", "Other")
        self.currency_combobox = ttk.Combobox(self.data_entry_frame, values=currency_options, state="readonly")
        self.currency_combobox.set("Credstick")
        # event to show/hide below two based on combobox string
        self.currency_combobox.bind("<<ComboboxSelected>>", self.on_category_change)

        category_label = Label(self.data_entry_frame, text="Category")
        self.category_var = StringVar()
        self.category_var.set("Registered")
        # radio buttons if currency type is credstick
        self.category_radios = Frame(self.data_entry_frame)
        self.registered_radio = Radiobutton(self.category_radios,
                                            text="Registered",
                                            variable=self.category_var,
                                            value="Registered")
        self.certified_radio = Radiobutton(self.category_radios,
                                           text="Certified",
                                           variable=self.category_var,
                                           value="Certified")

        # grid the children now to save time
        self.registered_radio.grid(column=0, row=0)
        self.certified_radio.grid(column=1, row=0)

        # otherwise string entry
        self.category_entry = Entry(self.data_entry_frame)

        # rating spinbox, should only appear when it's a credstick
        self.forged_val = IntVar()
        self.forged_val.set(0)
        self.forged_checkbox = Checkbutton(self.data_entry_frame,
                                           text="Forged Credstick",
                                           variable=self.forged_val,
                                           command=self.on_check_marked)
        self.rating_label = Label(self.data_entry_frame, text="Rating")
        # should only show if above is checked
        self.rating_spinbox = Spinbox(self.data_entry_frame, from_=0, to=99, width=3)

        # integer-only entry for balance
        balance_label = Label(self.data_entry_frame, text="Balance")
        self.balance_entry = Entry(self.data_entry_frame)

        # checkbox for do_not_spend
        self.do_not_spend_box = Checkbutton(self.data_entry_frame, text="Do not spend")

        self.all_currencies.insert(END, "Miscellaneous Currency")

        # buttons
        self.buttons_frame = Frame(self)
        # button for new item + new window
        self.new_currency_button = Button(self.buttons_frame, text="New Currency")
        # button to transfer funds + new window
        self.transfer_currency_button = Button(self.buttons_frame, text="Transfer Funds")
        # button to delete selected currency
        self.delete_currency_button = Button(self.buttons_frame, text="Delete Selected")

        # grid to save time
        self.new_currency_button.grid(column=0, row=0, padx=2, pady=2)
        self.transfer_currency_button.grid(column=1, row=0, padx=2, pady=2)
        self.delete_currency_button.grid(column=2, row=0, padx=2, pady=2)

        # grids
        self.treasury_frame.grid(column=0, row=0, sticky=(N, S))
        self.data_entry_frame.grid(column=1, row=0, sticky=(N, S))
        self.all_currencies.grid(column=0, row=0)
        self.buttons_frame.grid(column=0, row=1)

        # grid data entry
        name_label.grid(column=0, row=0)
        self.name_entry.grid(column=1, row=0, sticky=EW)

        currency_label.grid(column=0, row=1)
        self.currency_combobox.grid(column=1, row=1, sticky=EW)

        category_label.grid(column=0, row=2)
        self.category_radios.grid(column=1, row=2, sticky=EW)

        self.forged_checkbox.grid(column=0, row=3, columnspan=2)

        balance_label.grid(column=0, row=5)
        self.balance_entry.grid(column=1, row=5, sticky=EW)

    def on_category_change(self, event):
        self.category_radios.grid_forget()
        self.category_entry.grid_forget()

        if self.currency_combobox.current() == 0:  # should be "Credstick"
            self.category_radios.grid(column=1, row=2, sticky=EW)
        else:
            self.category_entry.grid(column=1, row=2, sticky=EW)

    def on_check_marked(self):
        if self.forged_val.get() == 1:
            self.rating_label.grid(column=0, row=4)
            self.rating_spinbox.grid(column=1, row=4, sticky=W)
        else:
            self.rating_label.grid_forget()
            self.rating_spinbox.grid_forget()

    def reload_data(self):
        pass

    def on_switch(self):
        pass

    def load_character(self):
        for c in self.statblock.currencies:
            self.all_currencies.insert(END, c.properties["name"])

        self.all_currencies.insert(END, "Miscellaneous Currency")

