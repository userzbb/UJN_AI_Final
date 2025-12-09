from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text

class StatusBar(Widget):
    """
    A status bar widget that displays the current mode and game info.
    """
    
    mode = reactive("NORMAL")
    map_name = reactive("Unknown")
    player_pos = reactive((0, 0))

    COMPONENT_CLASSES = {"status-bar--normal", "status-bar--command", "status-bar--insert"}

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text;
    }
    
    .status-bar--normal {
        background: #7aa2f7; /* Blue-ish */
        color: black;
        text-style: bold;
    }
    
    .status-bar--command {
        background: #f7768e; /* Red-ish */
        color: black;
        text-style: bold;
    }
    
    .status-bar--insert {
        background: #9ece6a; /* Green-ish */
        color: black;
        text-style: bold;
    }
    """

    def render(self):
        # Determine style based on mode
        mode_class = "status-bar--normal"
        if self.mode == "COMMAND":
            mode_class = "status-bar--command"
        elif self.mode == "INSERT":
            mode_class = "status-bar--insert"
            
        mode_style = self.get_component_rich_style(mode_class)
        mode_text = Text(f" {self.mode} ", style=mode_style)
        
        # Info section
        info_text = Text(f" {self.map_name} | {self.player_pos[0]}:{self.player_pos[1]} ", style="dim")
        
        return Text.assemble(mode_text, info_text)
