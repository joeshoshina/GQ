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
