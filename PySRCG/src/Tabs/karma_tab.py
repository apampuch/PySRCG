from abc import ABC

from tkinter import *
from tkinter import ttk

from src import app_data
from src.GenModes.finalized import Finalized
from src.Tabs.notebook_tab import NotebookTab
from src.adjustment import Adjustment


class KarmaTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)

        self.not_finalized_frame = Frame(self)
        self.finalized_frame = Frame(self)

        # setup not_finalized_frame
        finalize_label = Label(self.not_finalized_frame, text="Press button to finalize character. This is permanent!")
        finalize_button = Button(self.not_finalized_frame, text="Finalize", command=self.finalize_click)

        # setup finalizedFrame
        karma_pool_label = Label(self.finalized_frame, text="Karma Pool")
        self.karma_pool_val_label = ttk.Label(self.finalized_frame,
                                              text="PLACEHOLDER",
                                              style="Red.TLabel")

        self.vcmd = (self.register(self.int_validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # spending karma
        spending_karma_frame = ttk.LabelFrame(self.finalized_frame, text="Karma Spending")

        self.karma_for_cash_var = IntVar(0)  # reset this when applying
        karma_for_cash_label = Label(spending_karma_frame, text="¥1000 = 1 Karma")
        karma_for_cash_minus_button = Button(spending_karma_frame, text="-", command=self.sell_karma_with_cash)
        karma_for_cash_amount_label = Label(spending_karma_frame, textvariable=self.karma_for_cash_var)
        karma_for_cash_plus_button = Button(spending_karma_frame, text="+", command=self.buy_karma_with_cash)
        # karma_for_cash_box = Entry(spending_karma_frame, textvariable=self.karma_for_cash_var, validate="key",
        #                            validatecommand=self.vcmd)

        self.cash_for_karma_var = IntVar(0)
        cash_for_karma_label = Label(spending_karma_frame, text="1 Karma = ¥250")
        cash_for_karma_minus_button = Button(spending_karma_frame, text="-", command=self.sell_cash_with_karma)
        cash_for_karma_amount_label = Label(spending_karma_frame, textvariable=self.cash_for_karma_var)
        cash_for_karma_plus_button = Button(spending_karma_frame, text="+", command=self.buy_cash_with_karma)
        # cash_for_karma_box = Entry(spending_karma_frame, textvariable=self.cash_for_karma_var, validate="key",
        #                            validatecommand=self.vcmd)

        # TODO check if the character is an adept for this
        self.karma_for_adept_var = IntVar(0)
        karma_for_adept_label = Label(spending_karma_frame, text="20 Karma = 1 adept point")
        karma_for_adept_minus_button = Button(spending_karma_frame, text="-")
        karma_for_adept_amount_label = Label(spending_karma_frame, textvariable=self.karma_for_adept_var)
        karma_for_adept_plus_button = Button(spending_karma_frame, text="+", command=self.buy_adept_points_with_karma)
        # karma_for_adept_box = Entry(spending_karma_frame, textvariable=self.karma_for_adept_var, validate="key",
        #                             validatecommand=self.vcmd)

        self.karma_for_edge_flaw_var = IntVar(0)
        karma_for_edge_flaw_label = Label(spending_karma_frame, text="Edges and Flaws NYI")
        karma_for_edge_flaw_minus_button = Button(spending_karma_frame, text="-")
        karma_for_edge_flaw_amount_label = Label(spending_karma_frame, textvariable=self.karma_for_edge_flaw_var)
        karma_for_edge_flaw_plus_button = Button(spending_karma_frame, text="+", command=self.buy_edge_points_with_karma)
        # karma_for_edge_flaw_box = Entry(spending_karma_frame, textvariable=self.karma_for_edge_flaw_var, validate="key",
        #                                 validatecommand=self.vcmd)

        karma_for_custom_var = IntVar(0)
        karma_for_custom_reason_var = StringVar()
        karma_for_custom_label = Label(spending_karma_frame, text="Custom Karma Spending")
        karma_for_custom_box = Entry(spending_karma_frame, textvariable=karma_for_custom_var, validate="key",
                                     validatecommand=self.vcmd)
        # karma_for_custom_reason = Text(spending_karma_frame, textvariable=karma_for_custom_reason_var)

        # grid spending karma
        karma_for_cash_label.grid(column=0, row=0)
        karma_for_cash_minus_button.grid(column=1, row=0)
        karma_for_cash_amount_label.grid(column=2, row=0)
        karma_for_cash_plus_button.grid(column=3, row=0)

        cash_for_karma_label.grid(column=0, row=1)
        cash_for_karma_minus_button.grid(column=1, row=1)
        cash_for_karma_amount_label.grid(column=2, row=1)
        cash_for_karma_plus_button.grid(column=3, row=1)

        karma_for_adept_label.grid(column=0, row=2)
        karma_for_adept_minus_button.grid(column=1, row=2)
        karma_for_adept_amount_label.grid(column=2, row=2)
        karma_for_adept_plus_button.grid(column=3, row=2)

        karma_for_edge_flaw_label.grid(column=0, row=3)
        karma_for_edge_flaw_minus_button.grid(column=1, row=3)
        karma_for_edge_flaw_amount_label.grid(column=2, row=3)
        karma_for_edge_flaw_plus_button.grid(column=3, row=3)

        # setting karma
        set_karma_frame = ttk.LabelFrame(self.finalized_frame, text="Set Karma")

        # total
        total_karma_label = Label(set_karma_frame, text="Total")

        self.total_karma_var = IntVar(0)
        total_karma_box = Entry(set_karma_frame, textvariable=self.total_karma_var, validate="key",
                                validatecommand=self.vcmd)
        total_karma_add_button = Button(set_karma_frame, text="Add", command=self.add_total_karma)
        total_karma_sub_button = Button(set_karma_frame, text="Remove", command=self.sub_total_karma)

        spent_karma_label = Label(set_karma_frame, text="Spent")
        spent_karma_amt = Label(set_karma_frame, text="NYI")

        available_karma_label = Label(set_karma_frame, text="Available")
        self.available_karma_amt = Label(set_karma_frame, text="BUGGED")  # should always be Karma gen mode

        kp_loss_var = IntVar(0)
        kp_loss_label = Label(set_karma_frame, text="KP Loss")
        kp_loss_box = Entry(set_karma_frame, textvariable=kp_loss_var, validate="key",
                            validatecommand=self.vcmd)

        total_karma_label.grid(column=0, row=0)
        total_karma_box.grid(column=1, row=0)
        total_karma_add_button.grid(column=2, row=0)
        total_karma_sub_button.grid(column=3, row=0)
        spent_karma_label.grid(column=0, row=1)
        spent_karma_amt.grid(column=1, row=1)
        available_karma_label.grid(column=0, row=2)
        self.available_karma_amt.grid(column=1, row=2)
        kp_loss_label.grid(column=0, row=3)
        kp_loss_box.grid(column=1, row=3)

        apply_button = Button(self.finalized_frame, text="Apply", command=self.apply_click)  # needs command
        reset_button = Button(self.finalized_frame, text="Reset", command=self.reset_click)  # needs command

        finalize_label.pack()
        finalize_button.pack()

        set_karma_frame.pack(side=TOP)
        spending_karma_frame.pack(side=TOP)
        apply_button.pack(side=LEFT)
        reset_button.pack(side=RIGHT)

        karma_pool_label.pack()
        self.karma_pool_val_label.pack()

        self.not_finalized_frame.pack(expand=True)

    def int_validate(self, action, index, value_if_allowed,
                     prior_value, text, validation_type, trigger_type, widget_name):
        """
        Validates if entered text can be an int and over 0.
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
        if value_if_allowed == "":
            return True

        if value_if_allowed:
            try:
                i = int(value_if_allowed)
                if i > 0:
                    return True
                else:
                    self.bell()
                    return False
            except ValueError:
                self.bell()
                return False
        else:
            self.bell()
            return False

    def finalize_click(self):
        """
        have a "karma_adjustments" object *SOMEWHERE* for each thing that can be bought with karma
        karma_adjustments keeps track of increases to things, decreases can be made to "undo" increasees
        but not below the initial values from the karma tab, can either "finalize" or "reset"
        "reset" gets rid of all adjustments
        "finalize" sets all initial values to adjustments, spends karma permanently,
        then erases adjustments without undoing (since they've been finalized)
        """

        self.statblock.gen_mode = Finalized()
        self.statblock.gen_mode.update_total()
        self.karma_pool_val_label.configure(textvariable=self.gen_mode.karma_pool)
        self.on_switch()

    def apply_click(self):
        """
        Applies all changes from adjustments permanently.
        This gets the total karma of all adjustments, adds it to the applied karma value, then deletes all adjustments
        without invoking their undo() function.
        :return: None
        """
        total_adjustment_value = self.statblock.gen_mode.adjustments.total
        applied_karma_value = self.statblock.gen_mode.applied_karma.get()
        self.gen_mode.applied_karma.set(total_adjustment_value + applied_karma_value)
        self.gen_mode.adjustments.container.clear()

    def reset_click(self):
        """
        Resets all adjustments made and refunds all karma.
        :return:
        """
        self.gen_mode.adjustments.reset()

    def add_total_karma(self):
        """Adds the amount of good karma in the box to the character's good karma."""
        # validate that we have a positive amount
        if self.total_karma_var.get() < 0:
            print("Can't add negative amounts!")
            return

        self.statblock.gen_mode.add_karma(self.total_karma_var.get(), self.statblock.race)
        self.statblock.gen_mode.update_total()
        
    def sub_total_karma(self):
        """Adds the amount of good karma in the box to the character's good karma."""
        # validate that we have a positive amount
        if self.total_karma_var.get() < 0:
            print("Can't subtract negative amounts!")
            return

        self.statblock.gen_mode.sub_karma(self.total_karma_var.get(), self.statblock.race)
        self.statblock.gen_mode.update_total()

    def buy_karma_with_cash(self):
        """
        Buys karma with cash. The karma is not actually added until finalized.
        :return:
        """
        if not self.validate_genmode():
            return

        # check if we have enough cash
        if self.statblock.pay_cash(1000):
            self.karma_for_cash_var.set(self.karma_for_cash_var.get() + 1)
            self.statblock.gen_mode.add_karma(1, self.statblock.race)
            self.statblock.gen_mode.update_total()
        else:
            print("Not enough cash!")

    def sell_karma_with_cash(self):
        """
        Undoes buying karma with cash.
        :return:
        """
        if not self.validate_genmode():
            return

        # check if we can sell any karma back
        if self.karma_for_cash_var.get() <= 0:
            print("Can't sell any more karma back!")
        else:
            self.karma_for_cash_var.set(self.karma_for_cash_var.get() - 1)
            # self.statblock.cash += 1000
            self.statblock.add_cash(1000)
            self.statblock.gen_mode.sub_karma(1, self.statblock.race)
            self.statblock.gen_mode.update_total()

    def buy_cash_with_karma(self):
        if not self.validate_genmode():
            return

        # check if we can afford 1 karma for 250 nuyen
        if self.gen_mode.point_purchase_allowed(1, None):
            def undo():
                self.cash_for_karma_var.set(self.cash_for_karma_var.get() - 250)

            # make the purchase
            adjustment = Adjustment(1, "buy_cash_with_karma",  undo)
            self.gen_mode.add_adjustment(adjustment)
            self.cash_for_karma_var.set(self.cash_for_karma_var.get() + 250)
            # self.statblock.cash += 250
            self.statblock.add_cash(250)
        else:
            print("Not enough karma!")

    def sell_cash_with_karma(self):
        if not self.validate_genmode():
            return

        # check if we can sell back
        if self.cash_for_karma_var.get() >= 250:
            if self.statblock.pay_cash(250):
                self.gen_mode.undo("buy_cash_with_karma")
            else:
                print("Not enough cash left!")
        else:
            print("Can't sell any more cash back!")

    # TODO test this
    def buy_adept_points_with_karma(self):
        if not self.validate_genmode():
            return

        # check if we can afford it
        if self.gen_mode.point_purchase_allowed(20, None):
            def undo():
                self.cash_for_karma_var.set(self.karma_for_adept_var.get() - 1)

            # make the purchase
            adjustment = Adjustment(20, "buy_adept_point_with_karma",  undo)
            self.gen_mode.add_adjustment(adjustment)
            self.karma_for_adept_var.set(self.karma_for_adept_var.get() + 1)
            self.statblock.bonus_power_points += 1
        else:
            print("Not enough karma!")

    # TODO test this
    def sell_adept_points_with_karma(self):
        if not self.validate_genmode():
            return

        # check if we can sell back
        if self.karma_for_adept_var.get() <= 0:
            print("Can't sell any more karma back!")
        else:
            if self.statblock.total_power_points - self.statblock.power_points:  # check if we have enough
                self.statblock.bonus_power_points -= 1
            else:
                print("Not enough power points available!")

    def buy_edge_points_with_karma(self):
        if not self.validate_genmode():
            return

        # check if we can afford it
        # if self.gen_mode.point_purchase_allowed(20, None):
        #     def undo():
        #         self.cash_for_karma_var.set(self.karma_for_edge_flaw_var - 1)
        #
        #     # make the purchase
        #     adjustment = Adjustment(1, "buy_cash_with_karma",  undo)
        #     self.gen_mode.add_adjustment(adjustment)
        #     self.cash_for_karma_var.set(self.karma_for_edge_flaw_var + 1)
        else:
            print("Not enough karma!")

    def validate_genmode(self):
        if type(self.gen_mode) != Finalized:
            print("Genmode is not finalized!")
            return False
        else: 
            return True

    def on_switch(self):
        # show finalized frame if finalized, non finalized if not
        self.not_finalized_frame.pack_forget()
        self.finalized_frame.pack_forget()
        if type(self.statblock.gen_mode) == Finalized:
            self.finalized_frame.pack()
            self.available_karma_amt.config(textvariable=self.statblock.gen_mode.total_karma)
        else:
            self.not_finalized_frame.pack(expand=True)

    def load_character(self):
        self.on_switch()
