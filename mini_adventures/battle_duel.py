import random
from collections import deque

from .base_adventure import BaseAdventure
from guild_quest_subsystem.enums import LootType
from guild_quest_subsystem.character import LootTransaction
from guild_quest_subsystem.inventory import Item

MAX_HP = 30

_BLADE_PROC_CHANCE  = 0.40
_CLOAK_PROC_CHANCE  = 0.35
_CHARM_PROC_CHANCE  = 0.50

_TROPHY_ITEM = Item(
    "Duelist's Trophy",
    item_type="Trophy",
    rarity="Rare",
    description="Awarded to the victor of a Battle Duel.",
)

_ROLL_COMMANDS = {"roll", " ", "\n", "\r"}


def _calc_max_hp(level: int) -> int:
    return min(MAX_HP, 4 + level * 2)


class BattleDuelAdventure(BaseAdventure):
    NAME = "Battle Duel"
    DESCRIPTION = "Turn-based dice duel - roll to attack, last one standing wins!"

    def __init__(self, profile1, profile2):
        self._profiles = [profile1, profile2]

        self._hp: list[int] = [0, 0]
        self._max_hp: list[int] = [0, 0]
        self._inventories: list = [None, None]
        self._charm_used: list[bool] = [False, False]

        self._active_player_index: int = 0
        self._combat_log: deque[str] = deque(maxlen=6)
        self._result: str | None = None
        self._winner_index: int | None = None

        self.start()

    def start(self) -> None:
        for i, profile in enumerate(self._profiles):
            level = profile.character.get_level()
            self._max_hp[i] = _calc_max_hp(level)
            self._hp[i] = self._max_hp[i]
            self._inventories[i] = profile.character.get_inventory()
            self._charm_used[i] = False

        self._active_player_index = 0
        self._combat_log = deque(["Duel begins! Player 1's turn."], maxlen=6)
        self._result = None
        self._winner_index = None

    def handle_input(self, player_index: int, command: str) -> None:
        if self._result is not None:
            return
        if player_index != self._active_player_index:
            return
        if command not in _ROLL_COMMANDS:
            return

        self._do_roll(player_index)

    def update(self) -> None:
        pass

    def get_state(self) -> dict:
        players_snapshot = [
            {
                "name":   profile.username,
                "hp":     self._hp[i],
                "max_hp": self._max_hp[i],
            }
            for i, profile in enumerate(self._profiles)
        ]

        active_name = self._profiles[self._active_player_index].username

        state = {
            "adventure_name":      self.NAME,
            "players":             players_snapshot,
            "active_player_index": self._active_player_index,
            "active_player_name":  active_name,
            "result":              self._result,
            "winner_final_state":  None,
            "combat_log":          list(self._combat_log),
        }
        if self._result is not None:
            state["winner_final_state"] = self._build_winner_final_state()
        return state

    def is_complete(self) -> bool:
        return self._result is not None

    def reset(self) -> None:
        self.start()

    def _do_roll(self, attacker_index: int) -> None:
        defender_index = 1 - attacker_index
        attacker_name = self._profiles[attacker_index].username
        defender_name = self._profiles[defender_index].username

        roll = random.randint(1, 6)
        damage = roll
        event_parts = []

        if self._inventories[attacker_index].has_item("Mystic Blade"):
            if random.random() < _BLADE_PROC_CHANCE:
                damage += 1
                event_parts.append("Mystic Blade +1")

        if self._inventories[defender_index].has_item("Starlight Cloak"):
            if random.random() < _CLOAK_PROC_CHANCE:
                damage = max(1, damage - 1)
                event_parts.append("Starlight Cloak -1")

        new_hp = self._hp[defender_index] - damage
        charm_triggered = False

        if new_hp <= 0 and self._inventories[defender_index].has_item("Guardian Charm"):
            if not self._charm_used[defender_index]:
                if random.random() < _CHARM_PROC_CHANCE:
                    new_hp = 1
                    charm_triggered = True
                    self._charm_used[defender_index] = True
                    event_parts.append("Guardian Charm saved!")

        self._hp[defender_index] = max(0, new_hp)

        desc = (
            f"{attacker_name} rolled {roll} → {damage} dmg to {defender_name} "
            f"(HP {self._hp[defender_index]}/{self._max_hp[defender_index]})"
        )
        if event_parts:
            desc += "  [" + ", ".join(event_parts) + "]"
        if charm_triggered:
            desc += f"  {defender_name} clings to life!"

        self._combat_log.append(desc)

        if self._hp[defender_index] <= 0:
            self._winner_index = attacker_index
            self._record_results(attacker_index, attacker_name)
            return

        self._active_player_index = defender_index
        self._combat_log.append(f"Now it's {defender_name}'s turn.")

    def _record_results(self, winner_index: int, winner_name: str) -> None:
        loser_index = 1 - winner_index
        loser_name = self._profiles[loser_index].username

        winner_profile = self._profiles[winner_index]
        loser_profile  = self._profiles[loser_index]

        LootTransaction(LootType.GRANT, _TROPHY_ITEM, 1).apply(winner_profile.character)

        winner_character = winner_profile.character
        winner_character.set_level(winner_character.get_level() + 1)

        winner_profile.record_result(self.NAME, won=True)
        loser_profile.record_result(self.NAME, won=False)

        self._result = (
            f"{winner_name} defeats {loser_name}! "
            f"Reward: Duelist's Trophy | {winner_name} leveled up to {winner_character.get_level()}."
        )
        self._combat_log.append(self._result)

    def _build_winner_final_state(self) -> dict | None:
        if self._winner_index is None:
            return None

        winner_profile = self._profiles[self._winner_index]
        character = winner_profile.character
        return {
            "username":  winner_profile.username,
            "level":     character.get_level(),
            "inventory": character.get_inventory().to_list(),
        }