class GameData:
    def __init__(self):
        self.data_list = []

    def __getitem__(self, key):
        final_list = {}

        # TODO sort data_list by release date
        for book in self.data_list:
            if key in book.keys():
                final_list.update(book[key])

        return final_list

    def __contains__(self, item):
        raise NotImplementedError()

    def add(self, book):
        self.data_list.append(book)
