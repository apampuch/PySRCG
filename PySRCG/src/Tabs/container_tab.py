from tkinter import ttk

from src import app_data


class ContainerTab(ttk.Notebook):
    def __init__(self, parent):
        """
        :type tab_list: List(NoteBookTab)
        :type name_list: List(str)
        """
        super().__init__(parent)

        self.bind("<<NotebookTabChanged>>", app_data.window.on_tab_changed)

        self.tabs = []

    def add_tabs(self, tab_list, name_list):
        # confirm that they're the same length
        if len(tab_list) != len(name_list):
            raise ValueError("Tab list and name list must be of same length!")

        for i in range(0, len(tab_list)):
            self.tabs.append(tab_list[i])
            self.add(self.tabs[i], text=name_list[i])

    def on_switch(self):
        for tab in self.tabs:
            tab.on_switch()

    def load_character(self):
        for tab in self.tabs:
            tab.load_character()
