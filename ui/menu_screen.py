from .base_screen import BaseScreen
from .models import MenuOption, MenuState, ScreenEvent
import curses
from typing import Iterable, Optional, Sequence


class MenuScreen(BaseScreen):
    def __init__(
        self,
        stdscr: "curses.window",
        options: Optional[Iterable[str]] = None,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        highlight_pair: int = 1,
        menu_state: Optional[MenuState] = None,
        emit_events: bool = False,
    ) -> None:
        super().__init__(stdscr)
        self._emit_events = emit_events
        self._options: Sequence[MenuOption] = ()
        self._title = title
        self._subtitle = subtitle
        self._help_text = "Use Arrows to navigate — Enter to select"
        self._idx = 0
        self._highlight_pair = highlight_pair
        if menu_state is not None:
            self.set_state(menu_state)
        else:
            legacy_options = list(options or ())
            if not legacy_options:
                raise ValueError("MenuScreen requires at least one option")
            self._options = [MenuOption(id=opt, label=opt) for opt in legacy_options]

    def on_enter(self) -> None:
        try:
            curses.curs_set(0)
        except Exception:
            pass
        try:
            self.stdscr.keypad(True)
        except Exception:
            pass
        self._init_colors()


    def set_state(self, state: MenuState) -> None:
        super().set_state(state)
        self._title = state.title
        self._subtitle = state.subtitle
        self._options = list(state.options)
        self._help_text = state.help_text
        if self._options:
            self._idx = max(0, min(state.selected_index, len(self._options) - 1))
        else:
            self._idx = 0

    def _init_colors(self) -> None:
        if not curses.has_colors():
            return
        try:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(self._highlight_pair, curses.COLOR_WHITE, curses.COLOR_BLUE)
            curses.init_pair(self._highlight_pair + 1, curses.COLOR_CYAN, -1)
        except Exception:
            pass

    def _color_pair(self, pair_number: int) -> int:
        if not curses.has_colors():
            return curses.A_NORMAL
        try:
            return curses.color_pair(pair_number)
        except Exception:
            return curses.A_NORMAL

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

    # ── render ───────────────────────────────────────────────────────

    def render(self) -> None:
        self.stdscr.erase()
        max_y, _ = self.stdscr.getmaxyx()
        top_y = max(1, max_y // 6)

        if self._title:
            attr = curses.A_BOLD | self._color_pair(self._highlight_pair + 1)
            self._draw_centered(top_y, self._title, attr)

        if self._subtitle:
            self._draw_centered(top_y + 1, self._subtitle, curses.A_DIM)

        options = list(self._options)
        if not options:
            self._draw_centered(max_y // 2, "No options available", curses.A_DIM)
            self.stdscr.refresh()
            return

        menu_top = max(top_y + 3, max_y // 2 - len(options))
        for i, opt in enumerate(options):
            y = menu_top + i * 2
            if i == self._idx and opt.enabled:
                attr = self._color_pair(self._highlight_pair) | curses.A_BOLD
                self._draw_centered(y, opt.label, attr)
            else:
                attr = curses.A_DIM if not opt.enabled else curses.A_NORMAL
                self._draw_centered(y, opt.label, attr)

        self._draw_centered(max_y - 2, self._help_text, curses.A_DIM)
        self.stdscr.refresh()

    def handle_key(self, key: int) -> Optional[object]:
        if not self._options:
            return None
        if key == curses.KEY_UP:
            self._idx = (self._idx - 1) % len(self._options)
            if self._emit_events:
                return ScreenEvent(name="menu.move", payload={"delta": -1})
            return None
        if key == curses.KEY_DOWN:
            self._idx = (self._idx + 1) % len(self._options)
            if self._emit_events:
                return ScreenEvent(name="menu.move", payload={"delta": 1})
            return None
        if key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            selected = self._options[self._idx]
            if not selected.enabled:
                return None
            if self._emit_events:
                return ScreenEvent(name="menu.select", payload={"option_id": selected.id})
            return selected.label
        return None
