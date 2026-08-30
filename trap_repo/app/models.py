"""Simple in-memory data models for items."""

import uuid
from datetime import datetime, timezone


class Item:
    def __init__(self, name: str, description: str = "", price: float = 0.0):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.price = price
        self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "created_at": self.created_at,
        }


class ItemStore:
    """In-memory store for items."""

    def __init__(self):
        self._items: dict[str, Item] = {}

    def list_all(self) -> list[dict]:
        return [item.to_dict() for item in self._items.values()]

    def get(self, item_id: str) -> Item | None:
        return self._items.get(item_id)

    def create(self, name: str, description: str = "", price: float = 0.0) -> Item:
        item = Item(name=name, description=description, price=price)
        self._items[item.id] = item
        return item

    def delete(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def count(self) -> int:
        return len(self._items)
