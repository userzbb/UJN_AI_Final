from textual.widgets import Static
from rich.text import Text

class GameGrid(Static):
    """
    A widget that renders the game map.
    """
    
    def update_grid(self, grid_data: list[list[tuple[str, str]]]):
        """
        Updates the grid display.
        
        Args:
            grid_data: A 2D list (rows) of columns, where each cell is a tuple (symbol, color).
        """
        text = Text()
        for row in grid_data:
            for symbol, color in row:
                text.append(symbol, style=color)
            text.append("\n")
        
        self.update(text)
