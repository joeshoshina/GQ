from guild_quest_subsystem.character import Character
from guild_quest_subsystem.inventory import Inventory, Item
from guild_quest_subsystem.enums import LootType
from guild_quest_subsystem.character import LootTransaction

class PlayerProfile:
    """
    Persistent player profile for the GMAE.
    ------
    username        : display name chosen at login/register
    character       : Character instance (name, class, level)
    wins / losses   : overall W/L record
    achievements    : list of unlocked achievement strings
    quest_history   : list of (adventure_name, result) tuples
    preferred_realm : str name of their favourite realm
    """

    def __init__(self, username: str, character_class: str = "Adventurer",
                 preferred_realm: str = "The Starting Lands"):
        self.username = username
        self.character = Character(username, character_class, level=1)
        self.wins = 0
        self.losses = 0
        self.achievements: list[str] = []
        self.quest_history: list[tuple[str, str]] = []
        self.preferred_realm = preferred_realm

    def record_result(self, adventure_name: str, won: bool) -> None:
        result = "Victory" if won else "Defeat"
        self.quest_history.append((adventure_name, result))
        if won:
            self.wins += 1
            self._maybe_level_up()
        else:
            self.losses += 1
        self._check_achievements()

    def _maybe_level_up(self):
        if self.wins > 0 and self.wins % 3 == 0:
            self.character.set_level(self.character.get_level() + 1)

    def _check_achievements(self):
        total = self.wins + self.losses
        milestones = {
            1:  "First Quest",
            5:  "Seasoned Adventurer",
            10: "Veteran of the Realm",
        }
        win_milestones = {
            1:  "First Victory",
            5:  "Champion",
            10: "Legendary Hero",
            15: "The GOAT"
        }
        for threshold, name in milestones.items():
            if total >= threshold and name not in self.achievements:
                self.achievements.append(name)
        for threshold, name in win_milestones.items():
            if self.wins >= threshold and name not in self.achievements:
                self.achievements.append(name)

    def grant_item(self, item_name: str, quantity: int = 1) -> None:
        item = Item(item_name)
        tx = LootTransaction(LootType.GRANT, item, quantity)
        tx.apply(self.character)

    def get_inventory(self) -> Inventory:
        return self.character.get_inventory()

    def to_lines(self) -> list[str]:
        char = self.character
        lines = [
            f"  {char}",
            f"  Realm: {self.preferred_realm}",
            f"  W/L: {self.wins}/{self.losses}",
        ]
        if self.achievements:
            lines.append(f"  Achievements: {len(self.achievements)}")
            lines.append(f"    Latest: {self.achievements[-1]}")
        inv_entries = self.character.get_inventory().list_entries()
        if inv_entries:
            lines.append(f"  Items: {len(inv_entries)} type(s)")
        return lines

    def __str__(self):
        return (f"Profile[{self.username}] "
                f"{self.character} | W:{self.wins} L:{self.losses}")
