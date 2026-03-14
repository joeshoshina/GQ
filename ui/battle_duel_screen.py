import curses
from typing import Any, Optional

from .base_screen import BaseScreen
from .models import AdventureState, ScreenEvent
from mini_adventures.battle_duel import BattleDuelAdventure
from guild_quest_subsystem.inventory import Inventory
from profile import PlayerProfile


class BattleDuelScreen(BaseScreen):
    def __init__(self, stdscr: "curses.window") -> None:
        super().__init__(stdscr)
        self._adventure: BattleDuelAdventure | None = None
        self._state = AdventureState(screen_id="adventure", adventure_name="Battle Duel")
        self._last_game_state: dict[str, Any] = {}
        self._active_session_id = -1

    def on_enter(self) -> None:
        try:
            self.stdscr.keypad(True)
        except Exception:
            pass
        try:
            self.stdscr.timeout(200)
        except Exception:
            pass

    def set_state(self, state: AdventureState) -> None:
        super().set_state(state)
        self._state = state

        if state.session_id != self._active_session_id:
            self._active_session_id = state.session_id

            seed_state = dict(state.game_state) if state.game_state else {}
            player1_name = str(seed_state.get("player1_name", "Player 1"))
            player2_name = str(seed_state.get("player2_name", "Player 2"))
            player1_class = str(seed_state.get("player1_class", "Adventurer"))
            player2_class = str(seed_state.get("player2_class", "Adventurer"))
            player1_level = int(seed_state.get("player1_level", 1))
            player2_level = int(seed_state.get("player2_level", 1))
            player1_inventory = list(seed_state.get("player1_inventory", []))
            player2_inventory = list(seed_state.get("player2_inventory", []))

            profile1 = PlayerProfile(player1_name, character_class=player1_class)
            profile2 = PlayerProfile(player2_name, character_class=player2_class)
            profile1.character.set_level(player1_level)
            profile2.character.set_level(player2_level)
            self._restore_inventory(profile1, player1_inventory)
            self._restore_inventory(profile2, player2_inventory)

            self._adventure = BattleDuelAdventure(profile1, profile2)
            self._adventure.reset()
            self._last_game_state = self._adventure.get_state()
        elif state.game_state:
            self._last_game_state = dict(state.game_state)

    @staticmethod
    def _restore_inventory(profile: "PlayerProfile", inventory: list) -> None:
        restored = Inventory.from_list(inventory)
        char_inv = profile.character.get_inventory()
        char_inv.clear()
        for entry in restored.list_entries():
            char_inv.add(entry.get_item(), entry.get_quantity())

    def _draw_centered(self, y: int, text: str, attr: int = curses.A_NORMAL) -> None:
        max_y, max_x = self.stdscr.getmaxyx()
        if y < 0 or y >= max_y:
            return
        x = max(0, (max_x - len(text)) // 2)
        n = max(0, max_x - x - 1)
        if n > 0:
            try:
                self.stdscr.addnstr(y, x, text, n, attr)
            except curses.error:
                pass

    def _draw_at(self, y: int, x: int, text: str, attr: int = curses.A_NORMAL) -> None:
        max_y, max_x = self.stdscr.getmaxyx()
        if y < 0 or y >= max_y or x < 0 or x >= max_x:
            return
        n = max(0, max_x - x - 1)
        if n > 0:
            try:
                self.stdscr.addnstr(y, x, text, n, attr)
            except curses.error:
                pass

    def _build_event(self) -> ScreenEvent:
        self._adventure.update()
        self._last_game_state = self._adventure.get_state()
        payload = {
            "screen_id":      self._state.screen_id,
            "adventure_name": self._state.adventure_name,
            "game_state":     dict(self._last_game_state),
            "session_id":     self._state.session_id,
        }
        if self._adventure.is_complete():
            return ScreenEvent(name="adventure.complete", payload=payload)
        return ScreenEvent(name="adventure.update", payload=payload)

    def handle_key(self, key: int) -> Optional[object]:
        if self._adventure is None:
            return None

        if key == 27:
            return ScreenEvent(name="adventure.exit", payload={"screen_id": self._state.screen_id})

        if key == -1:
            return self._build_event()

        # P1 rolls
        if key in (ord(" "), ord("\n"), ord("\r"), curses.KEY_ENTER):
            self._adventure.handle_input(0, "roll")
        # P2 rolls
        elif key in (ord("p"), ord("P")):
            self._adventure.handle_input(1, "roll")
        else:
            return None

        return self._build_event()

    @staticmethod
    def _hp_bar(hp: int, max_hp: int, width: int = 8) -> str:
        if max_hp <= 0:
            return "░" * width
        filled = max(0, min(width, round(hp / max_hp * width)))
        return "█" * filled + "░" * (width - filled)

    def render(self) -> None:
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        game_state = self._last_game_state

        # Line 1 — adventure name (bold)
        title = game_state.get("adventure_name", self._state.adventure_name)
        self._draw_centered(1, title, curses.A_BOLD)

        self._draw_centered(2, "P1: Space/Enter  P2: P key  —  Esc to exit", curses.A_DIM)

        players = list(game_state.get("players", []))
        active_index = int(game_state.get("active_player_index", 0))
        active_name = str(game_state.get("active_player_name", ""))

        bar_top = 4
        left_margin = max(2, (max_x - 40) // 2)
        for idx, player in enumerate(players):
            name = str(player.get("name", f"Player {idx + 1}"))
            hp = int(player.get("hp", 0))
            max_hp = int(player.get("max_hp", 1))
            bar = self._hp_bar(hp, max_hp, width=8)
            line = f"{name}  HP: {hp}/{max_hp}  [{bar}]"
            attr = curses.A_BOLD if idx == active_index else curses.A_NORMAL
            self._draw_at(bar_top + idx, left_margin, line, attr)

        turn_row = bar_top + len(players) + 1
        if active_name:
            self._draw_centered(turn_row, f"Turn: {active_name}", curses.A_REVERSE)

        combat_log = list(game_state.get("combat_log", []))
        log_top = turn_row + 2
        last_i = len(combat_log) - 1
        for i, line in enumerate(combat_log[-6:]):
            log_row = log_top + i
            if log_row >= max_y - 3:
                break
            attr = curses.A_NORMAL if i == last_i else curses.A_DIM
            self._draw_centered(log_row, str(line), attr)

        result = game_state.get("result")
        if result:
            self._draw_centered(max_y - 3, str(result), curses.A_BOLD)

        self.stdscr.refresh()
