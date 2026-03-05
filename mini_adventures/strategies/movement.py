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