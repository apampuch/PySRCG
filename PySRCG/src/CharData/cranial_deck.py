from src.CharData.augment import Cyberware
from src.CharData.deck import Deck
from src.CharData.reportable import Reportable


class CranialDeck(Cyberware, Deck):
    def __init__(self, **kwargs):
        super(Deck, self).__init__()
        necessary_fields = ('legality', 'mpcp', 'cost', 'hardening', 'name', 'active_memory', 'io_speed',
                            'availability_rating', 'page', 'storage_memory', 'street_index', 'availability_unit',
                            'essence', 'response_increase', 'availability_time')

        self.fill_necessary_fields(necessary_fields, kwargs)

        # fields that should be added but not reported like holds/fits
        do_not_report = ["holds", "fits"]
        self.fill_miscellaneous_fields(kwargs, do_not_report)

        super(CranialDeck, self).setup_deck_stuff(kwargs)

    def serialize(self):
        ret_dict = self.properties.copy()
        ret_dict["stored_memory"] = []
        for obj in self.properties["stored_memory"]:
            ret_dict["stored_memory"].append(obj.serialize())
        return ret_dict
