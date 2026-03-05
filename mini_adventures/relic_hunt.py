import random
from base_adventure import BaseAdventure
from context import AdventureContext
from strategies.movement import GridMovement
from strategies.win_condition import RelicCountWin
from strategies.time_strategy import TurnBasedTime
from guild_quest_subsystem.inventory import Item
from guild_quest_subsystem.enums import LootType
from guild_quest_subsystem.character import LootTransaction
from guild_quest_subsystem.world_time import WorldTime
from guild_quest_subsystem.realm import Realm
from guild_quest_subsystem.time_rule import TimeRule
from typing import Set, Tuple

GRID_W = 12
GRID_H = 10
RELIC_COUNT = 5      
RELICS_NEEDED = 3    
MINUTES_PER_TURN = 15

_RELIC_ITEM = Item("Relic", item_type="Quest", rarity="Rare",
                   description="An ancient relic hidden in the realm.")


class RelicRaceAdventure(BaseAdventure):
    """
    Players:
        P1 keys: W/A/S/D
        P2 keys: ↑←↓→
    """

    NAME = "Relic Race"
    DESCRIPTION = "Competitive — race to collect 3 relics before your rival!"

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

        self._realm = Realm(
            name="The Shattered Wilds",
            description="Ruins where ancient relics lie scattered.",
            map_identity="shattered_wilds",
            time_rule=TimeRule(offset_minutes=120),
        )

    def start(self) -> None:
        p1 = self._make_player(self._profile1, x=0, y=0)
        p2 = self._make_player(self._profile2, x=GRID_W - 1, y=GRID_H - 1)

        ctx = AdventureContext(
            movement=GridMovement(),
            win_condition=RelicCountWin(),
            time_strategy=TurnBasedTime(MINUTES_PER_TURN),
        )
        ctx.grid_w = GRID_W
        ctx.grid_h = GRID_H
        ctx.blocked: set[tuple[int, int]] = self._generate_walls()
        ctx.relics: set[tuple[int, int]] = self._place_relics(
            ctx.blocked, [p1, p2]
        )
        ctx.players = [p1, p2]
        ctx.relics_needed = RELICS_NEEDED
        ctx.world_time = WorldTime(0, 6, 0) 
        self._ctx = ctx
        self._result = None

    def handle_input(self, player_index: int, command: str) -> None:
        if self._ctx is None or self._result is not None:
            return
        ctx = self._ctx

        if command in self.KEY_MAP:
            player_index, direction = self.KEY_MAP[command]
        else:
            direction = command
            if player_index not in (0, 1):
                return

        player = ctx.players[player_index]
        moved = ctx.move_player(player, direction)
        if moved:
            self._try_pick_up_relic(player)
            ctx.advance_time()
            self._result = ctx.check_winner()
            if self._result is not None:
                self._record_results()

    def update(self) -> None:
        pass

    def get_state(self) -> dict:
        if self._ctx is None:
            return {}
        ctx = self._ctx
        local = self._realm.to_local_time(ctx.world_time)
        return {
            "grid_w":   GRID_W,
            "grid_h":   GRID_H,
            "blocked":  ctx.blocked,
            "relics":   set(ctx.relics),
            "players":  [dict(p) for p in ctx.players],
            "result":   self._result,
            "world_time": str(ctx.world_time),
            "local_time": str(local),
            "realm":    self._realm.get_name(),
            "relics_needed": RELICS_NEEDED,
            "adventure_name": self.NAME,
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

    @staticmethod
    def _place_relics(blocked: set, players: list) -> set[tuple[int, int]]:
        occupied = blocked | {(p["x"], p["y"]) for p in players}
        rng = random.Random()
        relics: set[tuple[int, int]] = set()
        attempts = 0
        while len(relics) < RELIC_COUNT and attempts < 200:
            rx = rng.randint(0, GRID_W - 1)
            ry = rng.randint(0, GRID_H - 1)
            if (rx, ry) not in occupied:
                relics.add((rx, ry))
            attempts += 1
        return relics
    
    def _record_results(self) -> None:
        if self._ctx is None or self._result is None:
            return
        players = self._ctx.players
        winner_name = players[0]["name"] if players[0]["relics"] >= RELICS_NEEDED else players[1]["name"]
        for profile in (self._profile1, self._profile2):
            profile.record_result(self.NAME, won=(profile.username == winner_name))

    def _try_pick_up_relic(self, player: dict) -> None:
        pos = (player["x"], player["y"])
        if pos in self._ctx.relics:
            self._ctx.relics.discard(pos)
            player["relics"] += 1
            tx = LootTransaction(LootType.GRANT, _RELIC_ITEM, 1)
            tx.apply(player["character"])
