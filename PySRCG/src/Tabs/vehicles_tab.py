from abc import ABC

from src.Tabs.notebook_tab import NotebookTab


class VehiclesTab(NotebookTab, ABC):
    def __init__(self, parent):
        super().__init__(parent)
