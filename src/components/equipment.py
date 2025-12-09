from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class Equipment:
    """
    Component to store equipped items.
    """
    slots: Dict[str, Optional[str]] = field(default_factory=lambda: {
        "head": None,
        "body": None,
        "weapon": None,
        "accessory": None
    })

    def equip(self, slot: str, item_id: str):
        if slot in self.slots:
            self.slots[slot] = item_id

    def unequip(self, slot: str):
        if slot in self.slots:
            self.slots[slot] = None

    def get_item_id(self, slot: str) -> Optional[str]:
        return self.slots.get(slot)
