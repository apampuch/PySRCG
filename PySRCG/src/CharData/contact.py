class Contact:
    def __init__(self, name, location, archetype, affiliation, LTG, description, history):
        self.name = name
        self.location = location
        self.archetype = archetype
        self.affiliation = affiliation
        self.LTG = LTG
        self.description = description
        self.history = history

    def serialize(self):
        return self.__dict__
