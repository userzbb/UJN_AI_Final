from textual.screen import ModalScreen
from textual.widgets import Label, Button
from textual.containers import Container, Horizontal
from textual.binding import Binding
from textual.app import ComposeResult

class ConfirmationModal(ModalScreen):
    """
    A simple Yes/No confirmation modal.
    """
    
    DEFAULT_CSS = """
    ConfirmationModal {
        align: center middle;
        background: rgba(0,0,0,0.7);
    }
    
    #confirm-container {
        width: 40;
        height: auto;
        background: #1A1110;
        border: double #f7768e;
        padding: 1;
    }
    
    #confirm-message {
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
        color: #c0caf5;
    }
    
    #confirm-buttons {
        align: center middle;
        height: auto;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(id="confirm-container"):
            yield Label(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes (y)", variant="success", id="btn-yes")
                yield Button("No (n)", variant="error", id="btn-no")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_confirm(self):
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)
