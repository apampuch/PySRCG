from src.CharData.reportable import Reportable


class Credstick(Reportable):
    def __init__(self, name, registered_or_certified, registered_type, rating, balance=0):
        super().__init__()

        self.properties["name"] = name
        self.properties["registered_or_certified"] = registered_or_certified
        self.properties["registered_type"] = registered_type  # see sr3 p239
        self.properties["rating"] = rating  # 0 if legit, otherwise it's forged
        self.properties["balance"] = balance
