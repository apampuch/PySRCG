class GameData:
    def __init__(self):
        self.data_list = []

    # TODO don't make this rebuild every single time
    def __getitem__(self, key):
        final_list = {}

        # TODO sort data_list by release date
        for book in self.data_list:
            self.recursive_update(book, final_list, book["book"])
            # if key in book.keys():
            #     # this needs to recursively update everything so that a sub-dict doesn't override a parent dict
            #     final_list.update(book[key])

        return final_list[key]

    def __contains__(self, item):
        raise NotImplementedError()

    def recursive_update(self, book_dict, final_dict, book_name):
        """
        Recursively updates final_list from __getitem__
        @param book_dict: The (sub) dict of the book we're reading
        @param final_dict: The (sub) dict of the final data
        @param book_name: Book abbreviation of the book we're reading from
        @return: None
        """
        # get only the keys whose values are dicts
        keys_whose_values_are_dicts = list(filter(lambda x: type(book_dict[x]) == dict, book_dict.keys()))

        # iterate through each child in the book dict
        for book_key in keys_whose_values_are_dicts:
            book_sub_dict = book_dict[book_key]

            # if the book sub dict has a property named "page", add it to final_dict
            if "page" in book_sub_dict.keys():
                # add book abbreviation
                book_sub_dict["book"] = book_name
                final_dict[book_key] = book_sub_dict
            else:
                # if the final dict also has the key, we need to recurse down a layer
                # if it doesn't add it, then recurse down
                if book_key not in final_dict.keys():
                    final_dict[book_key] = {}
                self.recursive_update(book_sub_dict, final_dict[book_key], book_name)

    def add(self, book):
        self.data_list.append(book)
