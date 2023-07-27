from abc import ABC

from src.CharData.deck import Deck
from src.Tabs.three_column_buy_tab import ThreeColumnBuyTab

import src.app_data as app_data


class DeckBuyTab(ThreeColumnBuyTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "DeckBuyTab",
                         add_inv_callbacks=[parent.on_deck_change], remove_inv_callbacks=[parent.on_deck_change])

    @property
    def library_source(self):
        try:
            return app_data.game_data["Decks"]
        except KeyError:
            return {}

    @property
    def statblock_inventory(self):
        return self.statblock.decks

    @property
    def recurse_check_func(self):
        def decking_tab_recurse_check(val):
            return "cost" not in val.keys()

        return decking_tab_recurse_check

    @property
    def recurse_end_func(self):
        def decking_tab_recurse_end_callback(key, val, iid):
            # make it check if it's a part or a deck
            self.tree_item_dict[iid] = Deck(name=key, **val)

        return decking_tab_recurse_end_callback

    def buy_callback(self, selected):
        if app_data.pay_cash(selected.properties["cost"]):
            self.add_inv_item(selected)
        else:
            print("Not enough money!")

    def sell_callback(self, selected_index):
        selected_item = self.statblock_inventory[self.inv_selected_index]

        self.statblock.add_cash(selected_item.properties["cost"])

        self.remove_inv_item(selected_index)

    def on_switch(self):
        super().on_switch()

    def load_character(self):
        super().load_character()
