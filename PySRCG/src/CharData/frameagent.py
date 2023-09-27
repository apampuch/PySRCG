from src.CharData.program import Program
from src.CharData.software import Software


class FrameAgent(Software):
    def __init__(self, **kwargs):
        super().__init__()

        necessary_fields = ["cost", "bod", "evasion", "masking", "sensor", "frame_type", "utility_payload", "utilities"]
        necessary_fields = self.software_necessary_fields + necessary_fields

        # possible fields: "reaction", "initiative", "pilot_rating" if smart frame or agent
        if kwargs["frame_type"] in ("smart", "agent"):
            necessary_fields += ["initiative", "pilot_rating"]

        kwargs["cost"] = self.cost
        kwargs["size"] = self.size

        necessary_fields = tuple(necessary_fields)
        self.fill_necessary_fields(necessary_fields, kwargs)

    def size(self):
        return super().size() + sum(map(lambda soft: soft.size(), self.properties["utilities"]))

    def serialize(self):
        ret = self.properties.copy()

        ret["utilities"] = []
        for item in self.properties["utilities"]:
            ret["utilities"].append(item.serialize())

        del ret["size"]
        return ret

    def cost(self):
        if self.properties["rating"] == "rating":
            return "CHART NYI"
        elif self.properties["rating"] < 4:
            return 100 * self.size()
        elif 4 <= self.properties["rating"] < 7:
            return 200 * self.size()
        elif 7 <= self.properties["rating"] < 10:
            return 500 * self.size()
        else:
            return 1000 * self.size()


if __name__ == "__main__":
    test = FrameAgent(
        name="test",
        rating=1,
        multiplier=3,
        page=1,
        bod=1,
        evasion=1,
        masking=1,
        sensor=1,
        frame_type="dumb",
        utility_payload=1,
        utilities=[
            Program(
                name="test",
                rating=1,
                multiplier=3,
                page=1,
                cost=100,
                street_index=1,
                availability_rating=0,
                availability_time=0,
                availability_unit="Always"
            )
        ]
    )

    print(test.serialize())
