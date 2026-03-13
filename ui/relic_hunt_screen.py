"""
Adventure Gameplay Screen: Bridge Between UI and Game Logic.

This screen maps keyboard input to game commands and renders the adventure game state.

Key components:
- RelicHuntScreen: Inherits from BaseScreen; manages game loop and rendering
- _key_to_action(): Maps keyboard input to (player_index, direction) tuples
    - Player 1 (index 0): WASD keys
    - Player 2 (index 1): Arrow keys
- _render_grid(): Displays game board with player markers (1/2), walls (#), relics (*)
- handle_key(): Routes input to adventure logic, checks win condition, emits events
"""
import curses
from typing import Any, Optional, Tuple

from .base_screen import BaseScreen
from .models import AdventureState, ScreenEvent
from mini_adventures.relic_hunt import RelicRaceAdventure
from profile import PlayerProfile


class RelicHuntScreen(BaseScreen):
    def __init__(self, stdscr: "curses.window") -> None:
        super().__init__(stdscr)
        self._adventure: RelicRaceAdventure | None = None
        self._state = AdventureState(screen_id="adventure", adventure_name="Adventure")
        self._last_game_state: dict[str, Any] = {}
        self._active_session_id = -1

    def on_enter(self) -> None:
        try:
            self.stdscr.keypad(True)
        except Exception:
            pass
        try:
            self.stdscr.timeout(100)
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

            profile1 = PlayerProfile(player1_name, character_class=player1_class)
            profile2 = PlayerProfile(player2_name, character_class=player2_class)
            profile1.character.set_level(player1_level)
            profile2.character.set_level(player2_level)

            self._adventure = RelicRaceAdventure(profile1, profile2)
            self._adventure.reset()
            game_state = self._adventure.get_state()
            if isinstance(game_state, dict):
                self._last_game_state = game_state
        elif state.game_state:
            self._last_game_state = dict(state.game_state)

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

    def _key_to_action(self, key: int) -> Optional[Tuple[int, str]]:
        if key in (ord("w"), ord("W")):
            return (0, "up")
        if key in (ord("a"), ord("A")):
            return (0, "left")
        if key in (ord("s"), ord("S")):
            return (0, "down")
        if key in (ord("d"), ord("D")):
            return (0, "right")

        if key == curses.KEY_UP:
            return (1, "up")
        if key == curses.KEY_LEFT:
            return (1, "left")
        if key == curses.KEY_DOWN:
            return (1, "down")
        if key == curses.KEY_RIGHT:
            return (1, "right")
        return None

    def handle_key(self, key: int) -> Optional[object]:
        if self._adventure is None:
            return None

        if key == 27:
            return ScreenEvent(name="adventure.exit", payload={"screen_id": self._state.screen_id})

        if key == -1:
            self._adventure.update()
            game_state = self._adventure.get_state()
            if isinstance(game_state, dict):
                self._last_game_state = game_state

            payload = {
                "screen_id": self._state.screen_id,
                "adventure_name": self._state.adventure_name,
                "game_state": dict(self._last_game_state),
                "session_id": self._state.session_id,
            }
            if self._adventure.is_complete():
                return ScreenEvent(name="adventure.complete", payload=payload)
            return ScreenEvent(name="adventure.update", payload=payload)

        mapped = self._key_to_action(key)
        if mapped is None:
            return None

        player, action = mapped
        self._adventure.handle_input(player, action)
        self._adventure.update()
        game_state = self._adventure.get_state()
        if isinstance(game_state, dict):
            self._last_game_state = game_state

        payload = {
            "screen_id": self._state.screen_id,
            "adventure_name": self._state.adventure_name,
            "game_state": dict(self._last_game_state),
            "session_id": self._state.session_id,
        }

        if self._adventure.is_complete():
            return ScreenEvent(name="adventure.complete", payload=payload)
        return ScreenEvent(name="adventure.update", payload=payload)

    def _render_grid(self, top_y: int, left_x: int, game_state: dict[str, Any]) -> int:
        grid_w = int(game_state.get("grid_w", 0))
        grid_h = int(game_state.get("grid_h", 0))
        blocked = set(game_state.get("blocked", set()))
        relics = set(game_state.get("relics", set()))
        players = list(game_state.get("players", []))

        player_positions: dict[tuple[int, int], str] = {}
        for index, player in enumerate(players):
            marker = "1" if index == 0 else "2"
            player_positions[(player.get("x", -1), player.get("y", -1))] = marker

        for y in range(grid_h):
            row = []
            for x in range(grid_w):
                pos = (x, y)
                if pos in player_positions:
                    row.append(player_positions[pos])
                elif pos in blocked:
                    row.append("#")
                elif pos in relics:
                    row.append("*")
                else:
                    row.append(".")

            try:
                self.stdscr.addnstr(top_y + y, left_x, "".join(row), grid_w, curses.A_NORMAL)
            except curses.error:
                pass
        return grid_h

    def render(self) -> None:
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        s = self._state
        game_state = dict(s.game_state) if s.game_state else dict(self._last_game_state)

        title = game_state.get("adventure_name", s.adventure_name)
        self._draw_centered(1, title, curses.A_BOLD)

        active_name = str(game_state.get("active_player_name", ""))
        turn_remaining = float(game_state.get("turn_seconds_remaining", 0.0))
        turn_total = int(game_state.get("turn_seconds_total", 3))
        if active_name:
            self._draw_centered(2, f"Turn: {active_name} ({turn_remaining:.1f}/{turn_total}s)", curses.A_DIM)

        grid_w = int(game_state.get("grid_w", 0))
        left_x = max(0, (max_x - grid_w) // 2)
        grid_top = 4
        grid_h = 0
        if grid_w > 0:
            grid_h = self._render_grid(grid_top, left_x, game_state)
        else:
            self._draw_centered(max_y // 2, "Loading adventure...", curses.A_DIM)

        players = list(game_state.get("players", []))
        line_y = min(max_y - 4, grid_top + grid_h + 1)
        for index, player in enumerate(players):
            relics = player.get("relics", 0)
            line = f"P{index + 1} {player.get('name', 'Player')}: {relics} relic(s)"
            self._draw_centered(line_y + index, line)

        result = game_state.get("result")
        if result:
            self._draw_centered(max_y - 3, str(result), curses.A_BOLD)

        self._draw_centered(max_y - 2, s.help_text, curses.A_DIM)
        self.stdscr.refresh()