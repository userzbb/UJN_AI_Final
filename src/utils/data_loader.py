import json
import os
from typing import Dict
from src.data.models import Item

class GameDataLoader:
    _instance = None
    items: Dict[str, Item] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameDataLoader, cls).__new__(cls)
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        base_path = os.getcwd()
        items_path = os.path.join(base_path, "assets/data/items.json")
        
        try:
            with open(items_path, "r", encoding="utf-8") as f:
                items_data = json.load(f)
                for item_dict in items_data:
                    # Handle 'def' keyword conflict in stats if necessary, 
                    # but pydantic model uses 'def_' and json has 'def' usually?
                    # Let's assume json keys match model fields or we map them.
                    # The json example had "stats": {"atk": 15, "spd": -2}. No "def" yet.
                    item = Item(**item_dict)
                    self.items[item.id] = item
        except Exception as e:
            print(f"Error loading items: {e}")

    def get_item(self, item_id: str) -> Item:
        return self.items.get(item_id)

# Global instance
game_data = GameDataLoader()
