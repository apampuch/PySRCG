from copy import copy

from src.CharData.accessory import Accessory, Mount, VehicleWeapon


class Vehicle:
    def __init__(self, name, cost, availability_rating, availability_time, availability_unit, street_index,
                 handling_normal, handling_offroad, speed, accel, body, armor, sig, autonav, pilot, sensor, cargo, load, page, accessories=None,
                 **kwargs):
        self.name = name
        self.cost = cost
        self.availability_rating = availability_rating
        self.availability_time = availability_time
        self.availability_unit = availability_unit
        self.street_index = street_index
        self.handling_normal = handling_normal
        self.handling_offroad = handling_offroad
        self.speed = speed
        self.accel = accel
        self.body = body
        self.armor = armor
        self.sig = sig
        self.autonav = autonav
        self.pilot = pilot
        self.sensor = sensor
        self.cargo = cargo
        self.load = load
        self.page = page
        self.accessories = []

        # optional parts, like takeoff/seating
        self.optionals = kwargs

        if accessories is not None:
            for accessory in accessories:
                try:
                    if "recoil_compensation" in accessory.keys():
                        self.accessories.append(Mount(**accessory))
                    elif "damage" in accessory.keys():
                        self.accessories.append(VehicleWeapon(**accessory))
                    else:
                        self.accessories.append(Accessory(**accessory))
                except TypeError as e:
                    print("Error with {}:".format(accessories.name))
                    print(e)
                    print()

    def report(self) -> str:
        report_str = "{}\n\n".format(self.name)
        report_str += "Cost: {}\n".format(self.cost)
        report_str += "Availability: {}/{} {}\n".format(self.availability_rating, self.availability_time, self.availability_unit)
        report_str += "Street Index: {}\n".format(self.street_index)
        report_str += "Handling: {}".format(self.handling_normal)
        if not (self.handling_offroad == "NA" or self.handling_offroad is None):
            report_str += "/{}".format(self.handling_offroad)  # offroad handling
        report_str += "\nSpeed: {}\n".format(self.speed)
        report_str += "Accel: {}\n".format(self.accel)
        report_str += "Body: {}\n".format(self.body)
        report_str += "Armor: {}\n".format(self.armor)
        report_str += "Sig: {}\n".format(self.sig)
        report_str += "Autonav: {}\n".format(self.autonav)
        report_str += "Pilot: {}\n".format(self.pilot)
        report_str += "Sensor: {}\n".format(self.sensor)
        report_str += "Cargo: {}\n".format(self.cargo)
        report_str += "Load: {}\n".format(self.load)

        # all possible miscellaneous things that only some vehicles have go here
        report_str += self.report_if_exists("seating", "Seating")
        report_str += self.report_if_exists("entry_points", "Entry Points")
        report_str += self.report_if_exists("setup_breakdown", "Setup/Breakdown")
        report_str += self.report_if_exists("landing_takeoff", "Landing/Takeoff")

        if "other_features" in self.optionals.keys():
            report_str += "Other Features: "
            for feature in self.optionals["other_features"]:
                report_str += feature + ", "

            report_str.rstrip(", ")
            report_str += "\n"

        report_str += "Page: {}\n".format(self.page)

        # report accessories if they exist
        if len(self.accessories) > 0:
            report_str += "\nAcccessories:\n"
            for a in self.accessories:
                a_report = "\t" + a.report().replace("\n", "\n\t") + "\n\n"
                report_str += a_report

        return report_str

    def report_if_exists(self, key, name) -> str:
        if key in self.optionals.keys():
            return "{}: {}\n".format(name, self.optionals[key])
        else:
            return ""

    def serialize(self):
        ret_dict =  copy(self.__dict__)
        ret_dict["accessories"] = []
        for obj in self.accessories:
            ret_dict["accessories"].append(obj.__dict__)
        return ret_dict


# maybe just have one vehicle type and ensure not all fields are filled, with "vehicle type" 'enum'?
class GroundVehicle:
    pass


class Drone:
    pass
