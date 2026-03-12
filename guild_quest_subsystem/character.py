"""
Character and LootTransaction classes
"""
try:
    from .inventory import Inventory
    from .enums import LootType
except ImportError:
    from inventory import Inventory
    from enums import LootType


class Character:
    def __init__(self, name, character_class, level):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.inventory = Inventory()

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_character_class(self):
        return self.character_class

    def set_character_class(self, character_class):
        self.character_class = character_class

    def get_level(self):
        return self.level

    def set_level(self, level):
        self.level = level

    def get_inventory(self):
        return self.inventory

    def __str__(self):
        return f"{self.name} (Level {self.level} {self.character_class})"


class LootTransaction:

    def __init__(self, loot_type, item, quantity):
        self.loot_type = loot_type
        self.item = item
        self.quantity = quantity

    def get_type(self):
        return self.loot_type

    def get_item(self):
        return self.item

    def get_quantity(self):
        return self.quantity

    def apply(self, character):
        inventory = character.get_inventory()
        if self.loot_type == LootType.GRANT:
            inventory.add(self.item, self.quantity)
        elif self.loot_type == LootType.REMOVE:
            inventory.remove(self.item, self.quantity)

    def revert(self, character):
        inventory = character.get_inventory()
        if self.loot_type == LootType.GRANT:
            inventory.remove(self.item, self.quantity)
        elif self.loot_type == LootType.REMOVE:
            inventory.add(self.item, self.quantity)

    def __str__(self):
        return f"{self.loot_type.value} {self.quantity}x {self.item.get_name()}"
