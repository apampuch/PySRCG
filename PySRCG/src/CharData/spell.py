class Spell:
    def __init__(self, name, type, target, duration, drain, force, page):
        self.name = name
        self.type = type
        self.target = target
        self.duration = duration
        self.drain = drain
        self.force = force  # this only shows up on characters
        self.page = page

    def report(self) -> str:
        return "{}\n\n" \
               "Type: {}\n" \
               "Target: {}\n" \
               "Duration: {}\n" \
               "Cost: {}\n" \
               "Force: {}\n" \
               "Page: {}\n" \
            .format(self.name,
                    self.type,
                    self.target,
                    self.duration,
                    self.drain,
                    self.force,
                    self.page)

    def force_and_name(self):
        return "[{}] {}".format(self.force, self.name)

    def serialize(self):
        return self.__dict__
