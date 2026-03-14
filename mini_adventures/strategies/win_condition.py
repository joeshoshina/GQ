from abc import ABC, abstractmethod

class WinConditionStrategy(ABC):
    """
    Win Condition Strategies for GuildQuest Mini-Adventures.

    Defines interchangeable win-condition logic used by different
    mini-adventures.

    Strategy Pattern Role:
    WinConditionStrategy allows each adventure to define its own victory
    conditions without modifying the base adventure engine.

    Examples:
    - ReachTileWin: first player to reach a specific tile
    - RelicCollectionWin: first player to collect N relics
    - EscortSuccessWin: NPC safely reaches destination
    """
    
    @abstractmethod
    def check_winner(self, context):
        pass

class RelicCountWin(WinConditionStrategy):

    def check_winner(self, context) -> str | None:
        for p in context.players:
            if p["relics"] >= context.relics_needed:
                return f"{p['name']} wins by collecting {p['relics']} relics!"
        return None


class LastStandingWin(WinConditionStrategy):
    def check_winner(self, context) -> str | None:
        for p in context.players:
            if p.get("hp", 1) <= 0:
                survivors = [x for x in context.players if x.get("hp", 1) > 0]
                if survivors:
                    return f"{survivors[0]['name']} wins the duel!"
                return "Draw!"
        return None