from abc import ABC, abstractmethod

class MovementStrategy(ABC):
    """
    Movement Strategies for GuildQuest Mini-Adventures.

    This module defines the MovementStrategy interface and concrete
    movement behaviors used by mini-adventures.

    Strategy Pattern Role:
    MovementStrategy acts as the Strategy interface, allowing different
    movement mechanics (grid movement, teleportation, restricted paths, etc.)
    to be swapped without modifying the core adventure engine.

    Future developers can add new movement systems by implementing
    the MovementStrategy interface.
    """
    
    @abstractmethod
    def move(self, context, player, direction):
        pass

class GridMovement(MovementStrategy):
    DELTAS = {
        "up":    (0, -1),
        "down":  (0,  1),
        "left":  (-1, 0),
        "right": (1,  0),
    }

    def move(self, context, player: dict, direction: str) -> bool:
        dx, dy = self.DELTAS.get(direction, (0, 0))
        nx, ny = player["x"] + dx, player["y"] + dy

        if not (0 <= nx < context.grid_w and 0 <= ny < context.grid_h):
            return False

        if hasattr(context, "blocked") and (nx, ny) in context.blocked:
            return False

        player["x"] = nx
        player["y"] = ny
        return True
