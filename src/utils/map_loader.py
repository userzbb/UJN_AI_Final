from pathlib import Path

class Map:
    def __init__(self, width: int, height: int, tiles: list[list[str]]):
        self.width = width
        self.height = height
        self.tiles = tiles

def load_map_from_file(file_path: str) -> Map:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Map file not found: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip("\n") for line in f.readlines()]
    
    # Remove empty lines if any at the end
    lines = [line for line in lines if line]
    
    height = len(lines)
    width = max(len(line) for line in lines) if height > 0 else 0
    
    # Pad lines to ensure rectangular shape
    tiles = []
    for line in lines:
        tiles.append(list(line.ljust(width, " ")))
        
    return Map(width, height, tiles)
