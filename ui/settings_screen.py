import curses
from typing import Optional

from .base_screen import BaseScreen
from .models import SettingsState, ScreenEvent
from settings import Settings, ScoreDisplay


_SETTINGS_ROWS = [
    {
        "key": "score_display",
        "label": "Score Display",
        "enum": ScoreDisplay,
    },
]


class SettingsScreen(BaseScreen):
    def __init__(self, stdscr: "curses.window") -> None:
        super().__init__(stdscr)
        s = Settings.get_instance()
        self._state: SettingsState = SettingsState(
            screen_id="Settings",
            score_display=s.score_display.name,
        )
        self._pending: dict[str, object] = {
            "score_display": s.score_display,
        }
        self._active_row: int = 0
        self._saved: bool = False

    def on_enter(self) -> None:
        try:
            curses.curs_set(0)
        except Exception:
            pass
        try:
            self.stdscr.keypad(True)
        except Exception:
            pass

    def set_state(self, state: SettingsState) -> None:
        super().set_state(state)
        self._state = state
        try:
            self._pending["score_display"] = ScoreDisplay[state.score_display]
        except KeyError:
            pass

    def _draw_centered(self, y: int, text: str, attr: int = curses.A_NORMAL) -> None:
        max_y, max_x = self.stdscr.getmaxyx()
        if y < 0 or y >= max_y:
            return
        x = max(0, (max_x - len(text)) // 2)
        try:
            self.stdscr.addnstr(y, x, text, max_x - x - 1, attr)
        except curses.error:
            pass

    def _color(self, pair: int) -> int:
        if curses.has_colors():
            try:
                return curses.color_pair(pair)
            except Exception:
                pass
        return curses.A_NORMAL

    def render(self) -> None:
        self.stdscr.erase()
        max_y, _ = self.stdscr.getmaxyx()
        top_y = max(1, max_y // 6)

        self._draw_centered(top_y, "Settings", curses.A_BOLD)
        self._draw_centered(top_y + 1, "Configure your GuildQuest experience", curses.A_DIM)

        row_top = top_y + 4
        for i, row in enumerate(_SETTINGS_ROWS):
            y = row_top + i * 3
            label = row["label"]
            enum_cls = row["enum"]
            current_val: object = self._pending[row["key"]]

            # build the selector string:  < NUMERIC >
            members = list(enum_cls)
            idx = current_val.value
            prev_name = members[(idx - 1) % len(members)].name
            curr_name = current_val.name
            next_name = members[(idx + 1) % len(members)].name
            selector = f"< {curr_name} >"

            if i == self._active_row:
                label_attr = curses.A_BOLD | curses.A_REVERSE
                val_attr   = curses.A_BOLD | self._color(4)
            else:
                label_attr = curses.A_NORMAL
                val_attr   = curses.A_DIM

            self._draw_centered(y,     label,    label_attr)
            self._draw_centered(y + 1, selector, val_attr)

        status_y = row_top + len(_SETTINGS_ROWS) * 3 + 1
        if self._saved:
            self._draw_centered(status_y, "Settings saved!", self._color(1) | curses.A_BOLD)
        else:
            self._draw_centered(status_y, "Unsaved changes", self._color(2))

        if self._state.error:
            self._draw_centered(status_y + 1, self._state.error, self._color(3) | curses.A_BOLD)

        self._draw_centered(max_y - 2, self._state.help_text, curses.A_DIM)
        self.stdscr.refresh()

    def handle_key(self, key: int) -> Optional[ScreenEvent]:
        if key == 27:
            self._revert()
            return ScreenEvent(name="settings.back", payload={})

        if key in (curses.KEY_DOWN, ord("\t")):
            self._active_row = (self._active_row + 1) % len(_SETTINGS_ROWS)
            self._saved = False
            return None

        if key == curses.KEY_UP:
            self._active_row = (self._active_row - 1) % len(_SETTINGS_ROWS)
            self._saved = False
            return None

        if key in (curses.KEY_LEFT, ord("h")):
            self._cycle_current(-1)
            self._saved = False
            return None

        if key in (curses.KEY_RIGHT, ord("l")):
            self._cycle_current(1)
            self._saved = False
            return None

        if key in (ord("s"), ord("S"), curses.KEY_ENTER, ord("\n"), ord("\r")):
            self._commit()
            self._saved = True
            return ScreenEvent(
                name="settings.save",
                payload={"score_display": self._pending["score_display"].name},  # type: ignore[union-attr]
            )

        return None

    def _cycle_current(self, direction: int) -> None:
        row = _SETTINGS_ROWS[self._active_row]
        enum_cls = row["enum"]
        members  = list(enum_cls)
        current: object = self._pending[row["key"]]
        next_idx = (current.value + direction) % len(members)
        self._pending[row["key"]] = members[next_idx]

    def _commit(self) -> None:
        s = Settings.get_instance()
        s.score_display = self._pending["score_display"]
        self._state = SettingsState(
            screen_id="Settings",
            score_display=s.score_display.name,
        )

    def _revert(self) -> None:
        s = Settings.get_instance()
        self._pending["score_display"] = s.score_display
