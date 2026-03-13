"""
Relic Hunt Mini-Adventure - Competitive Relic Collection Gameplay.

Two players race on a grid-based realm to collect 3 magical relics and win.

Key components:
- RelicRaceAdventure: Concrete BaseAdventure implementation with relic collection mechanics
- Strategies injected via AdventureContext:
  - GridMovement: Handles movement with boundary and collision detection
  - RelicCountWin: Checks if player has collected 3+ relics
    - Turn timer: 3-second alternating player turns (P1 starts)
- Grid rendering: Walls (#), empty tiles (.), relics (*), players (1/2)
"""

import random
import time

from .base_adventure import BaseAdventure
from .context import AdventureContext
from .strategies.movement import GridMovement
from .strategies.win_condition import RelicCountWin
from guild_quest_subsystem.enums import LootType
from guild_quest_subsystem.character import LootTransaction
from guild_quest_subsystem.inventory import Item

GRID_W = 12
GRID_H = 10
RELICS_NEEDED = 3
TURN_SECONDS = 3

_RELIC_ITEM = Item("Relic", item_type="Quest", rarity="Rare",
                   description="An ancient relic hidden in the realm.")

_REWARD_ITEMS = (
    Item("Mystic Blade", item_type="Weapon", rarity="Rare", description="A shimmering blade of old."),
    Item("Guardian Charm", item_type="Trinket", rarity="Uncommon", description="A charm said to protect its bearer."),
    Item("Phoenix Feather", item_type="Crafting", rarity="Epic", description="Warm to the touch and faintly glowing."),
    Item("Starlight Cloak", item_type="Armor", rarity="Rare", description="A cloak woven with silver thread."),
)


class RelicRaceAdventure(BaseAdventure):
    """
    Players:
        P1 keys: W/A/S/D
        P2 keys: ↑←↓→
    """

    NAME = "Relic Race"
    DESCRIPTION = "Competitive - race to collect 3 relics before your rival!"

    KEY_MAP: dict[str, tuple[int, str]] = {
        #P1
        "w": (0, "up"),   "s": (0, "down"),
        "a": (0, "left"), "d": (0, "right"),
        #P2
        "up":    (1, "up"),   "down":  (1, "down"),
        "left":  (1, "left"), "right": (1, "right"),
    }

    def __init__(self, profile1, profile2):
        self._profile1 = profile1
        self._profile2 = profile2
        self._ctx: AdventureContext | None = None
        self._result: str | None = None
        self._last_reward_item: Item | None = None
        self._active_player_index: int = 0
        self._turn_deadline: float = 0.0

    def start(self) -> None:
        p1 = self._make_player(self._profile1, x=0, y=0)
        p2 = self._make_player(self._profile2, x=GRID_W - 1, y=GRID_H - 1)

        ctx = AdventureContext(
            movement=GridMovement(),
            win_condition=RelicCountWin(),
        )
        ctx.grid_w = GRID_W
        ctx.grid_h = GRID_H
        ctx.blocked = self._generate_walls()
        ctx.relics = set()
        ctx.players = [p1, p2]
        ctx.relics_needed = RELICS_NEEDED
        self._ctx = ctx
        self._result = None
        self._last_reward_item = None
        self._active_player_index = 0
        self._turn_deadline = time.monotonic() + TURN_SECONDS
        self._spawn_next_relic()

    def handle_input(self, player_index: int, command: str) -> None:
        if self._ctx is None or self._result is not None:
            return

        self._expire_turn_if_needed()
        ctx = self._ctx

        direction_commands = {"up", "down", "left", "right"}

        if command in direction_commands:
            direction = command
            if player_index not in (0, 1):
                return
        elif command in self.KEY_MAP:
            player_index, direction = self.KEY_MAP[command]
        else:
            direction = command
            if player_index not in (0, 1):
                return

        if player_index != self._active_player_index:
            return

        player = ctx.players[player_index]
        moved = ctx.move_player(player, direction)
        if moved:
            self._try_pick_up_relic(player)
            self._result = ctx.check_winner()
            if self._result is not None:
                self._record_results()

    def update(self) -> None:
        self._expire_turn_if_needed()

    def get_state(self) -> dict:
        if self._ctx is None:
            return {}
        ctx = self._ctx
        self._expire_turn_if_needed()
        turn_seconds_remaining = max(0.0, self._turn_deadline - time.monotonic())
        active_player_name = ""
        if 0 <= self._active_player_index < len(ctx.players):
            active_player_name = str(ctx.players[self._active_player_index].get("name", ""))
        return {
            "grid_w":   GRID_W,
            "grid_h":   GRID_H,
            "blocked":  ctx.blocked,
            "relics":   set(ctx.relics),
            "players":  [dict(p) for p in ctx.players],
            "result":   self._result,
            "relics_needed": RELICS_NEEDED,
            "adventure_name": self.NAME,
            "active_player_index": self._active_player_index,
            "active_player_name": active_player_name,
            "turn_seconds_remaining": turn_seconds_remaining,
            "turn_seconds_total": TURN_SECONDS,
        }

    def is_complete(self) -> bool:
        return self._result is not None

    def reset(self) -> None:
        self.start()

    @staticmethod
    def _make_player(profile, x: int, y: int) -> dict:
        profile.character.get_inventory().clear()
        return {
            "name":      profile.username,
            "character": profile.character,
            "x": x, "y": y,
            "relics": 0,
        }

    @staticmethod
    def _generate_walls() -> set[tuple[int, int]]:
        rng = random.Random()
        walls: set[tuple[int, int]] = set()
        for _ in range(14):
            wx = rng.randint(1, GRID_W - 2)
            wy = rng.randint(1, GRID_H - 2)
            walls.add((wx, wy))
        walls.discard((0, 0))
        walls.discard((GRID_W - 1, GRID_H - 1))
        return walls

    def _spawn_next_relic(self) -> None:
        if self._ctx is None:
            return
        ctx = self._ctx
        if ctx.relics:
            return

        occupied = set(ctx.blocked) | {(p["x"], p["y"]) for p in ctx.players}
        rng = random.Random()
        attempts = 0
        while attempts < 200:
            rx = rng.randint(0, GRID_W - 1)
            ry = rng.randint(0, GRID_H - 1)
            if (rx, ry) not in occupied:
                ctx.relics.add((rx, ry))
                return
            attempts += 1

    def _expire_turn_if_needed(self) -> None:
        if self._ctx is None or self._result is not None or not self._ctx.players:
            return
        now = time.monotonic()
        if now < self._turn_deadline:
            return
        elapsed_turns = int((now - self._turn_deadline) // TURN_SECONDS) + 1
        self._active_player_index = (self._active_player_index + elapsed_turns) % len(self._ctx.players)
        self._turn_deadline += elapsed_turns * TURN_SECONDS

    def _record_results(self) -> None:
        if self._ctx is None or self._result is None:
            return

        players = self._ctx.players
        winner_player = max(players, key=lambda player: player.get("relics", 0))
        winner_name = winner_player["name"]
        winner_profile = self._profile1 if winner_name == self._profile1.username else self._profile2

        reward_item = random.choice(_REWARD_ITEMS)
        self._last_reward_item = reward_item
        reward_tx = LootTransaction(LootType.GRANT, reward_item, 1)
        reward_tx.apply(winner_profile.character)

        winner_character = winner_profile.character
        winner_character.set_level(winner_character.get_level() + 1)

        self._result = (
            f"{winner_name} wins by collecting {winner_player.get('relics', 0)} relics! "
            f"Reward: {reward_item.get_name()} | {winner_name} leveled up to {winner_character.get_level()}."
        )

        for profile in (self._profile1, self._profile2):
            profile.record_result(self.NAME, won=(profile.username == winner_name))

    def _try_pick_up_relic(self, player: dict) -> None:
        if self._ctx is None:
            return

        pos = (player["x"], player["y"])
        if pos in self._ctx.relics:
            self._ctx.relics.discard(pos)
            player["relics"] += 1
            tx = LootTransaction(LootType.GRANT, _RELIC_ITEM, 1)
            tx.apply(player["character"])
            if player["relics"] < RELICS_NEEDED:
                self._spawn_next_relic()
