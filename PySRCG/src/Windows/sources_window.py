import os
from copy import copy
from pathlib import Path
from tkinter import *
from tkinter import filedialog

from src import app_data


class SourcesWindow(Toplevel):
    source_directory = Path.cwd() / "src/Assets/"
    selected_source_files = []
    valid_extensions = (".json",)

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Sources")

        # temporary list to replace selected source files with if we accept
        self.new_selected_source_files = copy(SourcesWindow.selected_source_files)

        # list of files in the directory, this should map 1:1 with the listbox
        self.file_list = []

        # grab focus and disable resizing
        self.grab_set()
        self.resizable(False, False)

        # text box for directory path
        self.path_var = StringVar()
        self.path_var.set(SourcesWindow.source_directory)
        path_label = Label(self, text="Sources Path:")
        self.path_entry = Entry(self, textvariable=self.path_var, width=60, state=DISABLED)
        browse_button = Button(self, text="Browse", command=lambda: self.browse_callback())

        # listbox for jsons
        # selected ones are used
        sources_labelframe = LabelFrame(self, text="Sources")
        self.sources_box = Listbox(sources_labelframe, selectmode=MULTIPLE, activestyle=NONE)
        self.sources_box.bind("<<ListboxSelect>>", self.selected_callback)

        # ok/cancel button
        ok_button = Button(self, text="OK", command=lambda: self.ok_callback())
        cancel_button = Button(self, text="Cancel", command=lambda: self.cancel_callback())

        # grids
        path_label.grid(column=0, row=0, padx=10)
        self.path_entry.grid(column=1, row=0, padx=10)
        browse_button.grid(column=2, row=0, padx=10, pady=5)

        sources_labelframe.grid(column=0, row=1, columnspan=3, sticky="WE", padx=10)
        self.sources_box.pack(fill=BOTH, padx=5, pady=5)

        ok_button.grid(column=0, row=2, pady=10)
        cancel_button.grid(column=2, row=2, pady=10)

        self.fill_listbox()

    # noinspection PyUnusedLocal
    def selected_callback(self, event):
        # updates selected source files list
        self.new_selected_source_files.clear()
        for index in self.sources_box.curselection():
            self.new_selected_source_files.append(self.file_list[index])

    def ok_callback(self):
        SourcesWindow.selected_source_files = copy(self.new_selected_source_files)

        # add all the data and load it
        app_data.window.load_game_data()

        # redo all the tabs' treeview loading bullshit
        all_tabs = app_data.menu.tabs()
        for tab in all_tabs:
            tab.reload_data()

        self.destroy()

    def cancel_callback(self):
        self.destroy()

    def browse_callback(self):
        new_path = filedialog.askdirectory()
        if new_path is not "":
            self.path_var.set(new_path)
            SourcesWindow.source_directory = Path(new_path)
            self.fill_listbox()

    def fill_listbox(self):
        """
        Fills the listbox self.sources_box full of the files in the directory.
        """
        # clear listbox
        self.sources_box.delete(0, END)

        for file in os.listdir(self.path_var.get()):
            for ending in SourcesWindow.valid_extensions:
                if file.endswith(ending):
                    # TODO open the json file and get the book and book_abbr properties and make the name from those
                    name = file

                    # add to the name file dict
                    self.sources_box.insert(END, name)

                    # index of the newly placed item is always the size of the thing minus one
                    self.file_list.append(file)

                    # select if it's already being used
                    if file in SourcesWindow.selected_source_files:
                        self.sources_box.selection_set(END)

    def validate_json(self, json_text):
        """
        Returns True if a json is valid for our purposes, False if it's not,
        :param json_text: Text of the json to validate
        """
        pass

    @staticmethod
    def first_setup():
        """
        Should only be called when first starting the program.
        This loads all of the default sources and selects them.
        :return:
        """
        for file in os.listdir(SourcesWindow.source_directory):
            for ending in SourcesWindow.valid_extensions:
                if file.endswith(ending):
                    SourcesWindow.selected_source_files.append(file)
