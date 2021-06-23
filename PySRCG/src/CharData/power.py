class Power:
    def __init__(self, name, cost, max_levels, page, level=1):
        self.name = name
        self.cost = cost
        self.level = level
        self.max_levels = max_levels
        self.page = page

    def serialize(self):
        return self.__dict__
