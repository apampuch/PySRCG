from src.CharData.reportable import Reportable


class Currency(Reportable):
    def __init__(self, name, currency_type, category, do_not_spend, rating=0, balance=0, permanent=False):
        """
        Anything that represents currency, be they credsticks
        :param name: Name, set by player.
        :param currency_type: Credstick, currency, scrip, or other.
        :param category: If a credstick, this field is either "registered" or "certified". Otherwise,
        the player sets this field.
        :param rating: Forged (registered) credsticks only.
        :param balance: The amount of this type of currency owned.
        :param permanent: If True, this can't be deleted, and most fields can't be edited.
        This should only be true for the miscellaneous cash thing.

        :type name: str
        :type currency_type: str
        :type category: str
        :type rating: int
        :type do_not_spend: bool
        :type balance: int
        :type permanent: bool
        """
        super().__init__()

        # validate currency_type
        valid_currency_types = ("Credstick", "Hard Currency", "Scrip",  "Other")
        if currency_type not in valid_currency_types:
            raise ValueError(f"{currency_type} not a valid currency type.")

        # input by player
        self.properties["name"] = name

        self.properties["currency_type"] = currency_type
        self.properties["category"] = category  # see sr3 p239
        self.properties["rating"] = rating  # 0 if legit, otherwise it's forged
        self.properties["do_not_spend"] = do_not_spend  # if True, don't spend from this
        self.properties["balance"] = balance
        self.properties["permanent"] = permanent
