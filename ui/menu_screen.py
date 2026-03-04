from .base_screen import BaseScreen
import curses
from typing import Optional, Iterable

class MenuScreen(BaseScreen):
    def __init__(
        self,
        stdscr: "curses.window",
        options: Iterable[str],
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        highlight_pair: int = 1,
    ) -> None:
        super().__init__(stdscr)
        self.options = list(options)
        if not self.options:
            raise ValueError("MenuScreen requires at least one option")
        self.title = title
        self.subtitle = subtitle
        self._idx = 0
        self._highlight_pair = highlight_pair
        if curses.has_colors():
            try:
                curses.use_default_colors()
                curses.init_pair(highlight_pair, curses.COLOR_WHITE, curses.COLOR_BLUE)
                curses.init_pair(highlight_pair + 1, curses.COLOR_CYAN, -1)
            except Exception:
                pass

    def render(self) -> None:
        self.stdscr.erase()
        max_y, _ = self.stdscr.getmaxyx()
        top_y = max(1, max_y // 6)
        if self.title:
            try:
                attr = curses.A_BOLD | self.color_pair(self._highlight_pair + 1)
                self.draw_centered(top_y, self.title, attr)
            except Exception:
                pass
        if self.subtitle:
            try:
                self.draw_centered(top_y + 1, self.subtitle, curses.A_DIM)
            except Exception:
                pass

        menu_top = max(top_y + 3, max_y // 2 - len(self.options))
        for i, opt in enumerate(self.options):
            y = menu_top + i * 2
            try:
                if i == self._idx:
                    attr = self.color_pair(self._highlight_pair) | curses.A_BOLD
                    self.draw_centered(y, opt, attr)
                else:
                    self.draw_centered(y, opt)
            except Exception:
                pass

        help_text = "Use Arrows to navigate — Enter to select"
        try:
            self.draw_centered(max_y - 2, help_text, curses.A_DIM)
        except Exception:
            pass

        try:
            self.stdscr.refresh()
        except Exception:
            pass

    def handle_key(self, key: int) -> Optional[str]:
        if key == curses.KEY_UP:
            self._idx = (self._idx - 1) % len(self.options)
            return None
        if key == curses.KEY_DOWN:
            self._idx = (self._idx + 1) % len(self.options)
            return None
        if key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            return self.options[self._idx]
        return None
