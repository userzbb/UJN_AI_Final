from textual.widgets import Input
from textual.binding import Binding
from textual.message import Message

class CommandLine(Input):
    """
    A command line input widget that appears at the bottom.
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    DEFAULT_CSS = """
    CommandLine {
        dock: bottom;
        height: 1;
        border: none;
        background: #1A1110;
        color: white;
        display: none; /* Hidden by default */
    }
    
    CommandLine:focus {
        border: none;
    }
    """
    
    def action_cancel(self):
        self.value = ""
        self.display = False
        self.post_message(self.Cancel(self))

    class Cancel(Message):
        """Sent when the user cancels the command line (Esc)."""
        def __init__(self, command_line: "CommandLine") -> None:
            self.command_line = command_line
            super().__init__()
