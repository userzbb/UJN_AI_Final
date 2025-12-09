from textual.screen import ModalScreen
from textual.widgets import ListView, ListItem, Label, Static, Markdown
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from textual.app import ComposeResult
from src.components.equipment import Equipment
from src.utils.data_loader import game_data
import esper

class EquipmentPicker(ModalScreen):
    """
    A Helix-style picker for viewing equipment and lore.
    """
    
    CSS_PATH = "../../assets/tcss/picker.tcss"
    
    BINDINGS = [
        Binding("escape", "close_picker", "Close"),
        Binding("space", "close_picker", "Close"),
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
    ]

    def __init__(self, player_entity):
        super().__init__()
        self.player_entity = player_entity
        self.equipment = esper.component_for_entity(self.player_entity, Equipment)

    def compose(self) -> ComposeResult:
        with Container(id="picker-container"):
            yield Label("EQUIPMENT / LORE", id="picker-title")
            
            with Horizontal(id="picker-content"):
                # Left: Slot List
                with Vertical(id="slot-list-container"):
                    yield ListView(id="slot-list")
                
                # Right: Item Details (Lore)
                with Vertical(id="item-details"):
                    yield Static(id="item-name")
                    yield Markdown(id="item-lore")
                    yield Static(id="item-stats")

    def on_mount(self):
        self._populate_slots()
        self.query_one("#slot-list").focus()

    def _populate_slots(self):
        list_view = self.query_one("#slot-list")
        
        # Define display order
        slots = ["head", "body", "weapon", "accessory"]
        
        for slot in slots:
            item_id = self.equipment.get_item_id(slot)
            item_name = "Empty"
            if item_id:
                item = game_data.get_item(item_id)
                if item:
                    item_name = item.name
            
            # Create a custom ID for the list item to track the slot
            list_item = ListItem(Label(f"{slot.upper():<10} : {item_name}"), id=f"slot-{slot}")
            list_view.append(list_item)

    def on_list_view_highlighted(self, message: ListView.Highlighted):
        """Update details when a slot is highlighted."""
        if message.item:
            slot = message.item.id.replace("slot-", "")
            self._show_item_details(slot)

    def _show_item_details(self, slot: str):
        item_id = self.equipment.get_item_id(slot)
        
        name_widget = self.query_one("#item-name")
        lore_widget = self.query_one("#item-lore")
        stats_widget = self.query_one("#item-stats")
        
        if item_id:
            item = game_data.get_item(item_id)
            if item:
                name_widget.update(f"[{item.color}]{item.name}[/]")
                lore_widget.update(f"**Description:**\n\n{item.description}")
                
                stats_text = "\nStats:\n"
                if item.stats:
                    if item.stats.atk: stats_text += f"ATK: {item.stats.atk} "
                    if item.stats.spd: stats_text += f"SPD: {item.stats.spd} "
                
                stats_widget.update(stats_text)
            else:
                name_widget.update("Unknown Item")
                lore_widget.update("")
                stats_widget.update("")
        else:
            name_widget.update("Empty Slot")
            lore_widget.update("_No equipment in this slot._")
            stats_widget.update("")

    def action_close_picker(self):
        self.dismiss()
    
    def action_cursor_down(self):
        self.query_one(ListView).action_cursor_down()
        
    def action_cursor_up(self):
        self.query_one(ListView).action_cursor_up()
