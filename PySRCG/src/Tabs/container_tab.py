from tkinter import ttk

from src import app_data


class ContainerTab(ttk.Notebook):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.name = name

        self.bind("<<NotebookTabChanged>>", app_data.window.on_tab_changed)

        self.tab_list = []

    def add_tabs(self, tab_list, name_list):
        # confirm that they're the same length
        if len(tab_list) != len(name_list):
            raise ValueError("Tab list and name list must be of same length!")

        for i in range(0, len(tab_list)):
            self.tab_list.append(tab_list[i])
            self.add(self.tab_list[i], text=name_list[i])

    def current_child(self):
        return app_data.root.nametowidget(self.select())

    def reload_data(self):
        for tab in self.tab_list:
            tab.reload_data()

    def on_switch(self):
        # we only need to on_switch the currently selected tab
        self.current_child().on_switch()

    def load_character(self):
        for tab in self.tab_list:
            tab.load_character()
