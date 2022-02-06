from tkinter import *
from tkinter import ttk


class SourcesWindow(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Sources")

        # grab focus and disable resizing
        self.grab_set()
        self.resizable(0, 0)

        # text box for directory path
        self.path_var = StringVar()
        path_label = Label(self, text="Sources Path:")
        self.path_entry = Entry(self, textvariable=self.path_var, width=60)
        browse_button = Button(self, text="Browse")

        # listbox for jsons
        # selected ones are used
        sources_labelframe = LabelFrame(self, text="Sources")
        self.sources_box = Listbox(sources_labelframe)

        # ok/cancel button
        ok_button = Button(self, text="OK", command=lambda: self.ok_callback())
        cancel_button = Button(self, text="Cancel", command=lambda: self.cancel_callback())

        # grids
        path_label.grid(column=0, row=0, padx=10)
        self.path_entry.grid(column=1, row=0, padx=10)
        browse_button.grid(column=2, row=0, padx=10, pady=5)

        sources_labelframe.grid(column=0, row=1, columnspan=3, sticky=(W, E), padx=10)
        self.sources_box.pack(fill=BOTH, padx=5, pady=5)

        ok_button.grid(column=0, row=2, pady=10)
        cancel_button.grid(column=2, row=2, pady=10)

    def ok_callback(self):
        pass

    def cancel_callback(self):
        pass

    def fill_listbox(self):
        pass

    def validate_json(self, json_text):
        """
        Returns True if a json is valid for our purposes, False if it's not,
        :param json_text: Text of the json to validate
        """
        pass