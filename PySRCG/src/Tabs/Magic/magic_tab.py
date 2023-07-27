from src import app_data
from src.Tabs.container_tab import ContainerTab


class MagicTab(ContainerTab):
    def __init__(self, parent):
        super().__init__(parent, "MagicTab")

        self.bind("<<NotebookTabChanged>>", app_data.window.on_tab_changed)

    def show_hide_tabs(self, awakened, tradition):
        # if no tradition, hide both tabs
        if tradition is None:
            self.tab(".!app.!magictab.!powerstab", state="hidden")
            self.tab(".!app.!magictab.!spellstab", state="hidden")
        # if an adept, always show powers
        elif tradition.name == "Adept":
            self.tab(".!app.!magictab.!powerstab", state="normal")

            # if aspected, hide spells
            if awakened == "Aspected":
                self.tab(".!app.!magictab.!spellstab", state="hidden")

            # otherwise, show spells
            else:
                self.tab(".!app.!magictab.!spellstab", state="normal")

        # otherwise, hide powers and show spells
        else:
            self.tab(".!app.!magictab.!powerstab", state="hidden")
            self.tab(".!app.!magictab.!spellstab", state="normal")
