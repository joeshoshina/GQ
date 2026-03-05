from abc import ABC, abstractmethod

class TimeStrategy(ABC):
    """
    Time progression strategies for GuildQuest Mini-Adventures.

    Strategy Pattern Role:
    Defines interchangeable time mechanics that control how world time
    advances during gameplay.

    This module integrates with the existing GuildQuest time subsystem
    (world_time.py) to allow mini-adventures to implement timed events,
    raid windows, or turn-based time progression.
    """

    @abstractmethod
    def advance_time(self, context):
        pass

class TurnBasedTime(TimeStrategy):

    def __init__(self, minutes_per_turn: int = 10):
        self.minutes_per_turn = minutes_per_turn

    def advance_time(self, context) -> None:
        context.world_time = context.world_time.add(self.minutes_per_turn)