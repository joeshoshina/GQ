from enum import Enum


class Visibility(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class PermissionLevel(Enum):
    VIEW = "VIEW"
    COLLABORATE = "COLLABORATE"


class Theme(Enum):
    LIGHT = "LIGHT"
    DARK = "DARK"
    AUTO = "AUTO"


class TimeDisplayPreference(Enum):
    WORLD_ONLY = "WORLD_ONLY"
    LOCAL_ONLY = "LOCAL_ONLY"
    BOTH = "BOTH"


class LootType(Enum):
    GRANT = "GRANT"
    REMOVE = "REMOVE"


class CharacterClass(Enum):
    WARRIOR  = "Warrior"
    MAGE     = "Mage"
    ROGUE    = "Rogue"
    CLERIC   = "Cleric"

    def description(self) -> str:
        return _CLASS_DESCRIPTIONS[self]


_CLASS_DESCRIPTIONS = {
    CharacterClass.WARRIOR: "A heavily armoured frontliner. High endurance, excels in melee combat.",
    CharacterClass.MAGE:    "A scholarly spellcaster. Fragile but commands devastating arcane power.",
    CharacterClass.ROGUE:   "A swift and cunning operative. Strikes hard from the shadows.",
    CharacterClass.CLERIC:  "A divine servant. Balances healing support with holy offensive magic.",
}
