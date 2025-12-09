from textual.screen import ModalScreen
from textual.widgets import ListView, ListItem, Label
from textual.containers import Container
from textual.binding import Binding
from textual.app import ComposeResult
from src.data.database import save_manager
from src.widgets.confirmation import ConfirmationModal

class SaveLoadPicker(ModalScreen):
    """
    Picker for Saving and Loading games.
    """
    
    CSS_PATH = "../../assets/tcss/picker.tcss"
    
    BINDINGS = [
        Binding("escape", "close_picker", "Close"),
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("d", "delete_save", "Delete"),
        Binding("o", "overwrite_save", "Overwrite"),
        Binding("l", "load_save", "Load"),
        Binding("enter", "select_item", "Select"),
    ]

    def __init__(self, current_state=None):
        super().__init__()
        self.current_state = current_state

    def compose(self) -> ComposeResult:
        with Container(id="picker-container"):
            title = "SAVE / LOAD (d:Del, l:Load)"
            if self.current_state:
                title += " (o:Over, Enter:New/Load)"
            yield Label(title, id="picker-title")
            yield ListView(id="save-list")

    def on_mount(self):
        self._populate_list()
        self.query_one("#save-list").focus()

    def _populate_list(self):
        list_view = self.query_one("#save-list")
        list_view.clear()
        
        # Option to create new save (Only if we have state to save)
        if self.current_state:
            list_view.append(ListItem(Label("[+] Create New Save"), id="action-new"))
        
        # List existing saves
        try:
            saves = save_manager.list_saves()
        except Exception as e:
            list_view.append(ListItem(Label(f"Error listing saves: {e}"), id="error-db"))
            return

        if not saves and not self.current_state:
             list_view.append(ListItem(Label("No saves found."), id="info-none"))

        for save in saves:
            s_id, timestamp, map_name = save
            label = f"[{s_id}] {timestamp} - {map_name}"
            list_view.append(ListItem(Label(label), id=f"save-{s_id}"))

    def action_close_picker(self):
        self.dismiss(None)

    def action_select_item(self):
        # Default action for Enter
        item = self.query_one(ListView).highlighted_child
        if not item: return
        
        if item.id == "action-new":
            self._request_new_save()
        elif item.id and item.id.startswith("save-"):
            self._request_load(item.id)

    def action_load_save(self):
        item = self.query_one(ListView).highlighted_child
        if item and item.id and item.id.startswith("save-"):
            self._request_load(item.id)

    def action_delete_save(self):
        item = self.query_one(ListView).highlighted_child
        if item and item.id and item.id.startswith("save-"):
            save_id = item.id.split("-")[1]
            self.app.push_screen(
                ConfirmationModal(f"Delete Save {save_id}?"),
                lambda res: self._do_delete(save_id) if res else None
            )

    def action_overwrite_save(self):
        if not self.current_state:
            self.notify("Cannot overwrite from Title Screen", severity="error")
            return

        item = self.query_one(ListView).highlighted_child
        if item and item.id and item.id.startswith("save-"):
            save_id = item.id.split("-")[1]
            self.app.push_screen(
                ConfirmationModal(f"Overwrite Save {save_id}?"),
                lambda res: self._do_overwrite(save_id) if res else None
            )

    def _request_new_save(self):
        self.app.push_screen(
            ConfirmationModal("Create New Save?"),
            lambda res: self._do_new_save() if res else None
        )

    def _request_load(self, item_id):
        save_id = int(item_id.split("-")[1])
        msg = f"Load Save {save_id}?"
        if self.current_state:
            msg += " Unsaved progress lost."
            
        self.app.push_screen(
            ConfirmationModal(msg),
            lambda res: self.dismiss(("load", save_id)) if res else None
        )

    def _do_delete(self, save_id):
        try:
            save_manager.delete_save(int(save_id))
            self.notify(f"Save {save_id} deleted.")
            self._populate_list()
        except Exception as e:
            import logging
            logging.basicConfig(filename='crash_delete.log', level=logging.ERROR)
            logging.exception("Crash in _do_delete")
            self.notify(f"Delete failed: {e}", severity="error")

    def _do_overwrite(self, save_id):
        save_manager.update_save(
            int(save_id),
            self.current_state["map_name"],
            self.current_state["player_pos"],
            self.current_state["equipment_slots"]
        )
        self.notify(f"Save {save_id} overwritten.")
        self._populate_list()

    def _do_new_save(self):
        save_manager.save_game(
            self.current_state["map_name"],
            self.current_state["player_pos"],
            self.current_state["equipment_slots"]
        )
        self.notify("New save created.")
        self._populate_list()
