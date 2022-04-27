from src.CharData.reportable import Reportable


class Currency(Reportable):
    def __init__(self, name, currency_type, category, rating, do_not_spend, balance=0):
        """
        Anything that represents currency, be they credsticks
        :param name: Name, set by player.
        :param currency_type: Credstick, currency, scrip, or other.
        :param category: If a credstick, this field is either "registered" or "certified". Otherwise,
        the player sets this field.
        :param rating: Forged (registered) credsticks only.
        :param balance: The amount of this type of currency owned.
        """
        super().__init__()

        # input by player
        self.properties["name"] = name

        self.properties["currency_type"] = currency_type
        self.properties["category"] = category  # see sr3 p239
        self.properties["rating"] = rating  # 0 if legit, otherwise it's forged
        self.properties["do_not_spend"] = do_not_spend  # if True, don't spend from this
        self.properties["balance"] = balance
