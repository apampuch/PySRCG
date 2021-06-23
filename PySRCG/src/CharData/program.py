class Program:  # might end up having to extend something like StorableInMemory
    def __init__(self, name, rating, multiplier, page, options=None):
        if options is None:
            options = {}

        # validate rating
        if rating != "rating" and rating < 1:
            raise ValueError("Rating must be at least 1")

        self.name = name
        self.rating = rating
        self.multiplier = multiplier
        self.options = options          # should be a list of a TBD object
        self.page = page

    def report(self) -> str:
        report_str = "{}\n\n".format(self.name)

        # if rating is just a string "rating", show rating-based things
        if self.rating == "rating":
            report_str +=   "Availability:\n" \
                            "    Rating 1-3: 2/7 days\n" \
                            "    Rating 4-6: 4/7 days\n" \
                            "    Rating 7-9: 8/14 days\n" \
                            "    Rating 10+: 16/30 days\n"

            report_str +=   "Cost:\n" \
                            "    Rating 1-3: 100 * rating\n" \
                            "    Rating 4-6: 200 * rating\n" \
                            "    Rating 7-9: 500 * rating\n" \
                            "    Rating 10+: 1000 * rating\n"

            report_str +=   "Street Index:\n" \
                            "    Rating 1-3: 1\n" \
                            "    Rating 4-6: 1.5\n" \
                            "    Rating 7-9: 2\n" \
                            "    Rating 10+: 3\n"

            report_str += "Size: Rating * Rating * Multiplier\n"
            report_str += "Multiplier: {}\n".format(self.multiplier)
            report_str += "Page: {}".format(self.page)
        else:
            report_str += "Availability: {}/{} {}\n" \
                          "Cost: {}\n" \
                          "Street Index: {}\n" \
                          "Rating: {}\n" \
                          "Multiplier: {}\n" \
                          "Size: {}\n" \
                          "Page: {}" \
                .format(self.availability_rating,
                        self.availability_time,
                        self.availability_unit,
                        self.cost,
                        self.street_index,
                        self.rating,
                        self.multiplier,
                        self.size,
                        self.page)

        return report_str

    @property
    def name_and_rating(self):
        return"{}: Rating {}".format(self.name, self.rating)

    @property
    def size(self):
        return self.rating * self.rating * self.multiplier

    @property
    def availability_rating(self):
        if self.rating == "rating":
            return "2-16"
        elif self.rating < 4:
            return 2
        elif 4 <= self.rating < 7:
            return 4
        elif 7 <= self.rating < 10:
            return 8
        else:
            return 16

    @property
    def availability_time(self):
        if self.rating == "rating":
            return "7-30"
        elif self.rating < 4:
            return 7
        elif 4 <= self.rating < 7:
            return 7
        elif 7 <= self.rating < 10:
            return 14
        else:
            return 30

    @property
    def availability_unit(self):
        return "days"

    @property
    def cost(self):
        if self.rating < 4:
            return 100 * self.size
        elif 4 <= self.rating < 7:
            return 200 * self.size
        elif 7 <= self.rating < 10:
            return 500 * self.size
        else:
            return 1000 * self.size

    @property
    def street_index(self):
        if self.rating < 4:
            return 1
        elif 4 <= self.rating < 7:
            return 1.5
        elif 7 <= self.rating < 10:
            return 2
        else:
            return 3

    def serialize(self):
        return self.__dict__
