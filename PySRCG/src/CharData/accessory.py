class Accessory:
    def __init__(self, name, cost, availability_rating, availability_time, availability_unit, street_index, legality,
                 page):
        self.name = name
        self.cost = cost
        self.availability_rating = availability_rating
        self.availability_time = availability_time
        self.availability_unit = availability_unit
        self.street_index = street_index
        self.legality = legality
        self.page = page

    def base_report(self) -> str:
        report_str = "{}\n\n".format(self.name)
        report_str += "Cost: {}\n".format(self.cost)
        report_str += "Availability: {}/{} {}\n".format(self.availability_rating, self.availability_time, self.availability_unit)
        report_str += "Street Index: {}\n".format(self.street_index)
        report_str += "Legality: {}\n".format(self.legality)

        return report_str

    def report(self) -> str:
        report_str = self.base_report()

        report_str += "Page: {}".format(self.page)
        return report_str

    def serialize(self):
        return self.__dict__


class Mount(Accessory):
    def __init__(self, name, cost, availability_rating, availability_time, availability_unit, street_index, legality,
                 page, cf_cost, load, recoil_compensation, body_cost):
        super().__init__(name, cost, availability_rating, availability_time, availability_unit, street_index, legality,
                         page)
        self.cf_cost = cf_cost
        self.load = load
        self.recoil_compensation = recoil_compensation
        self.body_cost = body_cost

    def report(self) -> str:
        report_str = self.base_report()
        report_str += "CF Cost: {}\n".format(self.cf_cost)
        report_str += "Load: {}\n".format(self.load)
        report_str += "Recoil Compensation: {}\n".format(self.recoil_compensation)

        report_str += "Page: {}".format(self.page)
        return report_str

    def serialize(self):
        return self.__dict__


class VehicleWeapon(Accessory):
    def __init__(self, name, cost, availability_rating, availability_time, availability_unit, street_index, legality,
                 page, type, ammo, mode, damage, weight):
        super().__init__(name, cost, availability_rating, availability_time, availability_unit, street_index, legality,
                         page)
        self.type = type
        self.ammo = ammo
        self.mode = mode
        self.damage = damage
        self.weight = weight

    def report(self) -> str:
        report_str = self.base_report()
        report_str += "Type: {}\n".format(self.type)
        report_str += "Ammo: {}\n".format(self.ammo)
        report_str += "Mode: {}\n".format(self.mode)
        report_str += "Damage: {}\n".format(self.damage)
        report_str += "Weight: {}\n".format(self.weight)

        report_str += "Page: {}".format(self.page)

        return report_str

    def serialize(self):
        return self.__dict__
