"""
Item and Inventory system classes
"""


class Item:
    
    def __init__(self, name, item_type=None, rarity=None, description=None):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.description = description
    
    def get_name(self):
        return self.name
    
    def __str__(self):
        result = self.name
        if self.rarity:
            result += f" [{self.rarity}]"
        if self.item_type:
            result += f" ({self.item_type})"
        return result
    
    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)


class InventoryEntry:
    
    def __init__(self, item, quantity):
        self.item = item
        self.quantity = max(0, quantity)
    
    def get_item(self):
        return self.item
    
    def get_quantity(self):
        return self.quantity
    
    def set_quantity(self, quantity):
        self.quantity = max(0, quantity)
    
    def increment(self, amount):
        self.quantity += amount
    
    def decrement(self, amount):
        self.quantity = max(0, self.quantity - amount)
    
    def __str__(self):
        return f"{self.item} x{self.quantity}"


class Inventory:
    
    def __init__(self):
        self.entries = []
    
    def add(self, item, quantity):
        existing = self._find_entry(item)
        if existing:
            existing.increment(quantity)
        else:
            self.entries.append(InventoryEntry(item, quantity))
    
    def remove(self, item, quantity):
        existing = self._find_entry(item)
        if existing:
            existing.decrement(quantity)
            if existing.get_quantity() == 0:
                self.entries.remove(existing)
    
    def set_quantity(self, item, quantity):
        existing = self._find_entry(item)
        if quantity <= 0:
            if existing:
                self.entries.remove(existing)
        else:
            if existing:
                existing.set_quantity(quantity)
            else:
                self.entries.append(InventoryEntry(item, quantity))
    
    def get_quantity(self, item):
        existing = self._find_entry(item)
        return existing.get_quantity() if existing else 0
    
    def list_entries(self):
        return list(self.entries)
    
    def _find_entry(self, item):
        for entry in self.entries:
            if entry.get_item() == item:
                return entry
        return None
    
    def __str__(self):
        if not self.entries:
            return "Empty inventory"
        return "\n".join(f"  {entry}" for entry in self.entries)
