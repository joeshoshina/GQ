import curses
import textwrap
from typing import Optional

from .base_screen import BaseScreen
from .models import AdventureResultState, MenuOption, ScreenEvent


class AdventureResultScreen(BaseScreen):
    def __init__(self, stdscr: "curses.window") -> None:
        super().__init__(stdscr)
        self._state: AdventureResultState = AdventureResultState(
            screen_id="AdventureResult",
            adventure_name="Adventure",
            result_text="",
        )

    def on_enter(self) -> None:
        try:
            curses.curs_set(0)
        except Exception:
            pass
        try:
            self.stdscr.keypad(True)
        except Exception:
            pass
        if curses.has_colors():
            try:
                curses.start_color()
                curses.use_default_colors()
                curses.init_pair(1, curses.COLOR_GREEN,  -1)   # victory
                curses.init_pair(2, curses.COLOR_YELLOW, -1)   # stats
                curses.init_pair(3, curses.COLOR_CYAN,   -1)   # highlight
            except Exception:
                pass

    def set_state(self, state: AdventureResultState) -> None:
        super().set_state(state)
        self._state = state

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

    def _color(self, pair: int) -> int:
        if curses.has_colors():
            try:
                return curses.color_pair(pair)
            except Exception:
                pass
        return curses.A_NORMAL


    def render(self) -> None:
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        s = self._state
        top_y = max(1, max_y // 8)

        # Title
        self._draw_centered(top_y, s.adventure_name, curses.A_BOLD)
        self._draw_centered(top_y + 1, "─── Result ───", curses.A_DIM)

        # Result text (may be long — wrap it)
        wrap_width = max(20, max_x - 4)
        wrapped = textwrap.wrap(s.result_text, width=wrap_width) if s.result_text else ["No result."]
        result_y = top_y + 3
        for i, line in enumerate(wrapped):
            self._draw_centered(result_y + i, line, curses.A_BOLD | self._color(1))

        # Stats lines
        stats_y = result_y + len(wrapped) + 2
        for i, line in enumerate(s.stats_lines):
            self._draw_centered(stats_y + i, line, self._color(2))

        # Options menu
        options = list(s.options)
        if options:
            options_top = stats_y + len(s.stats_lines) + 2
            idx = max(0, min(s.selected_index, len(options) - 1))
            for i, opt in enumerate(options):
                attr = curses.A_REVERSE | curses.A_BOLD if i == idx else curses.A_NORMAL
                self._draw_centered(options_top + i * 2, opt.label, attr)

        self._draw_centered(max_y - 2, s.help_text, curses.A_DIM)
        self.stdscr.refresh()

    def handle_key(self, key: int) -> Optional[ScreenEvent]:
        s = self._state
        options = list(s.options)
        if not options:
            return None

        if key == curses.KEY_UP:
            self._state = self._make_state(s, selected_index=(s.selected_index - 1) % len(options))
            return None

        if key == curses.KEY_DOWN:
            self._state = self._make_state(s, selected_index=(s.selected_index + 1) % len(options))
            return None

        if key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            idx = max(0, min(s.selected_index, len(options) - 1))
            selected = options[idx]
            return ScreenEvent(
                name="adventure_result.select",
                payload={"option_id": selected.id},
            )

        return None

    def _make_state(self, s: AdventureResultState, selected_index: int) -> AdventureResultState:
        return AdventureResultState(
            screen_id=s.screen_id,
            adventure_name=s.adventure_name,
            result_text=s.result_text,
            stats_lines=s.stats_lines,
            options=s.options,
            selected_index=selected_index,
            help_text=s.help_text,
        )
