import esper
from src.components.base import Position, Velocity
from src.utils.map_loader import Map

class MovementSystem(esper.Processor):
    def __init__(self, game_map: Map):
        self.game_map = game_map
        self.blocking_tiles = {"#", "+"} # Walls and closed doors block movement

    def process(self):
        for ent, (pos, vel) in esper.get_components(Position, Velocity):
            if vel.dx == 0 and vel.dy == 0:
                continue

            target_x = pos.x + vel.dx
            target_y = pos.y + vel.dy

            # Boundary check
            if 0 <= target_x < self.game_map.width and 0 <= target_y < self.game_map.height:
                # Collision check
                tile = self.game_map.tiles[target_y][target_x]
                
                # Treat '@' as floor for collision purposes if it's still in the map data
                if tile == "@":
                    tile = "."

                if tile not in self.blocking_tiles:
                    pos.x = target_x
                    pos.y = target_y
            
            # Reset velocity after move attempt
            vel.dx = 0
            vel.dy = 0
