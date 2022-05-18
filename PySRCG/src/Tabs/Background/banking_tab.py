from abc import ABC
from tkinter import *
from tkinter import ttk

from src.CharData.currency import Currency
from src.Tabs.notebook_tab import NotebookTab
from src.app_data import on_cash_updated

"""
NOTE: There is a bug that I can't seem to fix involving double clicking things that causes the listbox
to become deselected, and thus disable all of the UI elements. I don't know how to fix this.
"""

class BankingTab(NotebookTab, ABC):
    def selected_currency(self) -> Currency:
        return self.statblock.currencies[self.selected_currency_index]

    def __init__(self, parent):
        super().__init__(parent)

        # this should be set when clicking on the listbox
        # set to max when deleting last one
        self.selected_currency_index = -1

        # used to validate input
        self.vcmd = (self.register(self.int_validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        """
        This is a listbox for currencies. When a currency is clicked, the other boxes will auto-populate.
        Editing them will edit the currency.
        Pressing the "new currency" button will populate this box with a new currency that can be edited.
        Each item in the listbox maps to one Currency object in self.statblock.currencies
        The listbox will always be populated with a single "Miscellaneous Cash" object that does not map
        to a Currency, it instead represenes the misc_cash variable in the statblock.
        """
        self.treasury_frame = LabelFrame(self, text="Treasury", padx=5, pady=5)
        self.all_currencies = Listbox(self.treasury_frame, width=50, selectmode=BROWSE)
        self.all_currencies_scroll = Scrollbar(self.treasury_frame, orient=VERTICAL, command=self.all_currencies.yview)
        self.all_currencies["yscrollcommand"] = self.all_currencies_scroll.set
        self.all_currencies.bind("<<ListboxSelect>>", self.on_select_listbox)

        self.data_entry_frame = LabelFrame(self, text="Selected Item", padx=5, pady=5)
        self.data_entry_objs = CurrencyDataEntry(self.data_entry_frame, self.vcmd)

        self.all_currencies.insert(END, "Miscellaneous Currency")

        # buttons
        self.buttons_frame = Frame(self)
        # button for new item + new window
        self.new_currency_button = Button(self.buttons_frame, text="New Currency", command=self.new_currency)
        # button to transfer funds + new window
        self.transfer_currency_button = Button(self.buttons_frame, text="Transfer Funds")
        # button to delete selected currency
        self.delete_currency_button = Button(self.buttons_frame, text="Delete Selected", command=self.delete_currency)

        # grid to save time
        self.new_currency_button.grid(column=0, row=0, padx=2, pady=2)
        self.transfer_currency_button.grid(column=1, row=0, padx=2, pady=2)
        self.delete_currency_button.grid(column=2, row=0, padx=2, pady=2)

        # grids
        self.treasury_frame.grid(column=0, row=0, sticky=(N, S))
        self.data_entry_frame.grid(column=1, row=0, sticky=(N, S))
        self.all_currencies.grid(column=0, row=0)
        self.all_currencies_scroll.grid(column=1, row=0, sticky=(N, S))
        self.buttons_frame.grid(column=0, row=1)

        # final setup thing
        self.on_select_listbox(None)

    def new_currency(self):
        temp_window = Toplevel(self.parent)
        temp_window.grab_set()
        temp_window.resizable(0, 0)

        # make a new window with all of the selected item stuff
        new_currency_data_entry = CurrencyDataEntry(temp_window, self.vcmd)

        # if checked, pay for it if applicable
        pay_var = IntVar()
        pay_var.set(0)
        pay_checkbox = Checkbutton(temp_window,
                                   text="Pay for credstick",
                                   variable=pay_var)
        pay_checkbox.grid(column=0, row=6)

        def credistick_cost_rating(rating):
            if type(rating) is not int:
                raise ValueError("Rating must be an integer!")
            elif rating < 1:
                print("Rating less than 1, is free")
                return 0
            elif rating <= 4:
                return rating * rating * 1000
            elif rating <= 8:
                return rating * 5000
            elif rating <= 12:
                return rating * 10000
            else:
                return rating * 50000

        def ok_func():
            # prevent blank names
            if new_currency_data_entry.name_var.get() == "":
                self.bell()
                return

            temp_window.destroy()
            new_currency = Currency(new_currency_data_entry.name_var.get(),
                                    new_currency_data_entry.currency_type_var.get(),
                                    new_currency_data_entry.category_var.get(),
                                    False,
                                    new_currency_data_entry.true_rating(),
                                    new_currency_data_entry.balance_var.get())

            self.statblock.currencies.append(new_currency)

            # pay if we have to
            do_insert = True
            if bool(pay_var.get()):
                cost = credistick_cost_rating(new_currency_data_entry.true_rating())
                do_insert = self.statblock.pay_cash(cost)

            if do_insert:
                # add to listbox
                self.all_currencies.insert(END, new_currency.properties["name"])

                # refresh cash
                # TODO move the string update to a lambda in the event
                self.statblock.cash_str = "¥{}".format(self.statblock.cash)
                on_cash_updated()
            else:
                print("Can't afford that.")

        ok_button = Button(temp_window, text="OK", command=ok_func)
        ok_button.grid(column=0, row=7)

        def cancel_func():
            temp_window.destroy()

        cancel_button = Button(temp_window, text="Cancel", command=cancel_func)
        cancel_button.grid(column=1, row=7)

    def delete_currency(self):
        selection = self.all_currencies.curselection()
        # do nothing if nothing is selected
        if len(selection) == 0:
            return

        # there will only ever be one selected

        if self.selected_currency().properties["permanent"]:
            print("Can't delete that!")
            return

        # delete from inventory
        del self.statblock.currencies[self.selected_currency_index]
        self.all_currencies.delete(self.selected_currency_index)

        # update selected so we're not overshooting the array of currencies
        self.selected_currency_index = min(self.selected_currency_index, len(self.statblock.currencies) - 1)

        # update cash
        self.statblock.cash_str = "¥{}".format(self.statblock.cash)
        on_cash_updated()

    def on_select_listbox(self, event):
        print("yee")
        selection = self.all_currencies.curselection()

        if len(selection) > 0 and not self.statblock.currencies[selection[0]].properties["permanent"]:
            self.data_entry_objs.name_entry.configure(state=NORMAL)
            self.data_entry_objs.currency_combobox.configure(state="readonly")
            self.data_entry_objs.registered_radio.configure(state=NORMAL)
            self.data_entry_objs.certified_radio.configure(state=NORMAL)
            self.data_entry_objs.category_entry.configure(state=NORMAL)
            self.data_entry_objs.forged_checkbox.configure(state=NORMAL)
            self.data_entry_objs.balance_entry.configure(state=NORMAL)
            self.delete_currency_button.configure(state=NORMAL)

        # disable everything if current selection is blank or de
        else:
            self.data_entry_objs.name_entry.configure(state=DISABLED)
            self.data_entry_objs.currency_combobox.configure(state=DISABLED)
            self.data_entry_objs.registered_radio.configure(state=DISABLED)
            self.data_entry_objs.certified_radio.configure(state=DISABLED)
            self.data_entry_objs.category_entry.configure(state=DISABLED)
            self.data_entry_objs.forged_checkbox.configure(state=DISABLED)
            self.delete_currency_button.configure(state=DISABLED)
            if len(selection) == 0:
                print(len(selection))
                self.data_entry_objs.balance_entry.configure(state=DISABLED)
            else:
                self.data_entry_objs.balance_entry.configure(state=NORMAL)

        if len(selection) > 0:
            self.selected_currency_index = selection[0]
            self.data_entry_objs.name_var.set(self.selected_currency().properties["name"])
            self.data_entry_objs.currency_type_var.set(self.selected_currency().properties["currency_type"])
            self.data_entry_objs.category_var.set(self.selected_currency().properties["category"])
            self.data_entry_objs.on_category_change(None)
            self.data_entry_objs.do_not_spend_var.set(self.selected_currency().properties["do_not_spend"])
            self.data_entry_objs.rating_var.set(self.selected_currency().properties["rating"])
            self.data_entry_objs.balance_var.set(self.selected_currency().properties["balance"])

    def int_validate(self, action, index, value_if_allowed,
                     prior_value, text, validation_type, trigger_type, widget_name):
        """
        Validates if entered text can be an int.
        :param action:
        :param index:
        :param value_if_allowed:
        :param prior_value:
        :param text:
        :param validation_type:
        :param trigger_type:
        :param widget_name:
        :return: True if text is valid
        """

        if value_if_allowed or value_if_allowed == "":
            try:
                if value_if_allowed == "":
                    val = 0
                else:
                    val = int(value_if_allowed)

                # just allow it if there's nothing there for some reason
                # this is to shut up an error when loading
                if len(self.all_currencies.curselection()) < 1:
                    return True

                self.selected_currency().properties["balance"] = val

                self.statblock.cash_str = "¥{}".format(self.statblock.cash)
                on_cash_updated()
                return True
            except ValueError:
                self.bell()
                return False
        else:
            self.bell()
            return False

    def reload_data(self):
        pass

    def on_switch(self):
        pass

    def load_character(self):
        for c in self.statblock.currencies:
            self.all_currencies.insert(END, c.properties["name"])

        self.all_currencies.insert(END, "Miscellaneous Currency")


class CurrencyDataEntry:
    """
    Separate class to make reusing some code easier.
    """
    def __init__(self, parent, vcmd):
        self.parent = parent
        self.vcmd = vcmd
        name_label = Label(parent, text="Name")
        self.name_var = StringVar()
        self.name_entry = Entry(parent, width=30, textvariable=self.name_var)

        # currency type combobox
        currency_label = Label(parent, text="Currency")
        currency_options = ("Credstick", "Currency", "Scrip", "Other")
        self.currency_type_var = StringVar()
        self.currency_combobox = ttk.Combobox(parent, values=currency_options, state="readonly",
                                              textvariable=self.currency_type_var)
        self.currency_combobox.set("Credstick")
        # event to show/hide below two based on combobox string
        self.currency_combobox.bind("<<ComboboxSelected>>", self.on_category_change)

        category_label = Label(parent, text="Category")
        self.category_var = StringVar()
        self.category_var.set("Registered")
        # radio buttons if currency type is credstick
        self.category_radios = Frame(parent)
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
        self.category_entry = Entry(parent)

        # rating spinbox, should only appear when it's a credstick
        self.forged_val = IntVar()
        self.forged_val.set(0)
        self.forged_checkbox = Checkbutton(parent,
                                           text="Forged Credstick",
                                           variable=self.forged_val,
                                           command=self.on_check_marked)
        self.rating_label = Label(parent, text="Rating")
        # should only show if above is checked
        self.rating_var = IntVar()
        self.rating_var.set(1)
        self.rating_spinbox = Spinbox(parent, from_=1, to=99, width=3, textvariable=self.rating_var)

        # integer-only entry for balance
        balance_label = Label(parent, text="Balance")
        self.balance_var = IntVar()
        self.balance_var.set(0)
        self.balance_entry = Entry(parent, textvariable=self.balance_var, validate="key", validatecommand=self.vcmd)

        # checkbox for do_not_spend
        self.do_not_spend_var = IntVar()
        self.do_not_spend_var.set(0)
        self.do_not_spend_box = Checkbutton(parent, text="Do not spend", variable=self.do_not_spend_var)

        # grid everything
        name_label.grid(column=0, row=0)
        self.name_entry.grid(column=1, row=0, sticky=EW)

        currency_label.grid(column=0, row=1)
        self.currency_combobox.grid(column=1, row=1, sticky=EW)

        category_label.grid(column=0, row=2)
        self.category_radios.grid(column=1, row=2, sticky=EW)

        self.forged_checkbox.grid(column=0, row=3, columnspan=2)

        balance_label.grid(column=0, row=5)
        self.balance_entry.grid(column=1, row=5, sticky=EW)

    def true_rating(self):
        f = self.forged_val.get()
        if not bool(f):
            return 0
        else:
            return self.rating_var.get()

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
