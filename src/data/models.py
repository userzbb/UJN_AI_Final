from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ItemStats(BaseModel):
    atk: Optional[int] = 0
    def_: Optional[int] = 0
    spd: Optional[int] = 0
    hp: Optional[int] = 0
    ep: Optional[int] = 0

class ItemEffect(BaseModel):
    type: str
    condition: Optional[str] = None
    value: Any

class Item(BaseModel):
    id: str
    name: str
    symbol: str
    color: str
    type: str
    era: Optional[str] = None
    rarity: Optional[str] = "common"
    description: str
    stats: Optional[ItemStats] = None
    effects: Optional[List[ItemEffect]] = None
    use_effect: Optional[Dict[str, Any]] = None
    price: Optional[int] = 0
