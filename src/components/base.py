from dataclasses import dataclass

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Renderable:
    symbol: str
    color: str = "white"
    z_index: int = 0  # Higher z_index renders on top

@dataclass
class Player:
    """Tag component for the player"""
    pass

@dataclass
class Velocity:
    dx: int = 0
    dy: int = 0
