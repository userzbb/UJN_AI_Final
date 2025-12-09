from textual.screen import ModalScreen
from textual.widgets import ListView, ListItem, Label
from textual.containers import Container
from textual.binding import Binding
from textual.app import ComposeResult

class SpaceMenu(ModalScreen):
    """
    The initial menu opened by pressing Space.
    Acts as a dispatcher to other pickers.
    """
    
    CSS_PATH = "../../assets/tcss/picker.tcss"
    
    BINDINGS = [
        Binding("escape", "close_menu", "Close"),
        Binding("e", "open_equipment", "Equipment"),
        Binding("s", "open_save_load", "Save/Load"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="picker-container"):
            yield Label("ACTIONS", id="picker-title")
            yield ListView(id="menu-list")

    def on_mount(self):
        list_view = self.query_one("#menu-list")
        list_view.append(ListItem(Label("e : Equipment"), id="opt-equip"))
        list_view.append(ListItem(Label("s : Save / Load"), id="opt-save"))
        list_view.focus()

    def action_close_menu(self):
        self.dismiss()

    def action_open_equipment(self):
        self.dismiss("equipment")

    def action_open_save_load(self):
        self.dismiss("save_load")
    
    def on_list_view_selected(self, message: ListView.Selected):
        if message.item.id == "opt-equip":
            self.dismiss("equipment")
        elif message.item.id == "opt-save":
            self.dismiss("save_load")
