from abc import ABC

from src.Tabs.notebook_tab import NotebookTab


# should be hidden if character is not an otaku
class OtakuTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent, "OtakuTab")
        
    def reload_data(self):
        pass

    def on_switch(self):
        pass

    def load_character(self):
        pass
