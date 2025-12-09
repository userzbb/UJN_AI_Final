import esper
from src.components.base import Position, Renderable
from src.widgets.game_grid import GameGrid
from src.utils.map_loader import Map

# Palette from Design Doc
COLOR_BRASS = "#B5A642"
COLOR_RUST = "#8B4513"
COLOR_STEAM = "#F0F8FF"
COLOR_SOOT = "#1A1110"
COLOR_FLOOR = "#696969" # Dim Grey
COLOR_DOOR = "#8B4513" # Brownish

TILE_MAPPING = {
    "#": ("", COLOR_BRASS),
    ".": ("", COLOR_FLOOR),
    "+": ("", COLOR_DOOR),
    "~": ("", COLOR_STEAM),
    " ": (" ", COLOR_SOOT),
}

class RenderSystem(esper.Processor):
    def __init__(self, game_grid: GameGrid, game_map: Map):
        self.game_grid = game_grid
        self.game_map = game_map

    def process(self):
        # 1. Initialize grid with map tiles
        grid_data = []
        for y in range(self.game_map.height):
            row = []
            for x in range(self.game_map.width):
                char = self.game_map.tiles[y][x]
                # If the map file contains '@', we treat it as floor for rendering the background,
                # assuming the actual player entity is created separately.
                if char == "@":
                    char = "."
                
                symbol, color = TILE_MAPPING.get(char, (char, "white"))
                row.append((symbol, color))
            grid_data.append(row)

        # 2. Draw entities
        # Sort by z-index to ensure correct layering
        entities = []
        for ent, (pos, rend) in esper.get_components(Position, Renderable):
            entities.append((pos, rend))
        
        entities.sort(key=lambda x: x[1].z_index)

        for pos, rend in entities:
            if 0 <= pos.y < self.game_map.height and 0 <= pos.x < self.game_map.width:
                grid_data[pos.y][pos.x] = (rend.symbol, rend.color)

        # 3. Update widget
        self.game_grid.update_grid(grid_data)
