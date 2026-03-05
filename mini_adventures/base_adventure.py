from abc import ABC, abstractmethod

class BaseAdventure(ABC):
    """
    Base class that all mini-adventures must implement.

    Defines the lifecycle required by the GuildQuest
    Mini-Adventure Environment.
    """

    @abstractmethod
    def start(self):
        """Initialize the adventure."""
        pass

    @abstractmethod
    def handle_input(self, player, command):
        """Process player input."""
        pass

    @abstractmethod
    def update(self):
        """Advance the game state."""
        pass

    @abstractmethod
    def get_state(self):
        """Return the current state of the adventure."""
        pass

    @abstractmethod
    def is_complete(self):
        """Return True if the adventure is finished."""
        pass

    @abstractmethod
    def reset(self):
        """Reset the adventure."""
        pass