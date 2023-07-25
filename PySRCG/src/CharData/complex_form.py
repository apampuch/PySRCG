from src.CharData.software import Software


class ComplexForm(Software):
    def __init__(self, **kwargs):
        super().__init__()

        kwargs["size"] = self.size

        self.fill_necessary_fields(self.software_necessary_fields, kwargs)
        self.fill_miscellaneous_fields(kwargs)
