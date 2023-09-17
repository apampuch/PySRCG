from typing import List


class Specialization:
    def __init__(self, name, rank, attribute):
        self.name = name
        self.rank = rank
        self.attribute = attribute  # should always be same as parent

    def serialize(self):
        return {
            "name": self.name,
            "rank": self.rank,
            "attribute": self.attribute,
        }


class Skill:
    specializations: List[Specialization]

    def __repr__(self):
        return "{}: {}".format(self.name, self.rank)

    def __init__(self, name, attribute, rank, skill_type, book, page, specializations=None):
        if specializations is None:
            specializations = []
        self.name = name
        self.attribute = attribute
        self.rank = rank
        self.specializations = []
        for spec in specializations:
            self.specializations.append(Specialization(**spec))

        self.skill_type = skill_type
        self.book = book
        self.page = page

    def cost_to_increase(self):
        pass

    def serialize(self):
        return {
            "name": self.name,
            "attribute": self.attribute,
            "rank": self.rank,
            "specializations": list(map(lambda x: x.serialize(), self.specializations)),
            "skill_type": self.skill_type,
            "book": self.book,
            "page": self.page
        }
