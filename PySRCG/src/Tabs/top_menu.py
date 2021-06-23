import src.app_data as app_data
import src.char_io as char_io
from tkinter import *


class TopMenu(Menu):
    # set_character: 'function'
    # get_character: 'function'

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.file_menu = Menu(self)
        self.File = self.add_cascade(label="File", menu=self.file_menu)

        # self.get_character = None
        # self.set_character = None

        self.file_menu.add_command(label="New", command=lambda: char_io.new_char(self.tabs))
        self.file_menu.add_command(label="Open", command=lambda: char_io.load(self.tabs))
        self.file_menu.add_command(label="Save", command=lambda: char_io.save(app_data.app_character))
        self.file_menu.add_command(label="Save As", command=lambda: char_io.save_as(app_data.app_character))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Quit", command=parent.quit)

    def tabs(self):
        """Returns all tabs."""
        return self.parent.winfo_children()[2].winfo_children()
