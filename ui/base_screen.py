import abc
import curses
from typing import Optional, Sequence


class BaseScreen(abc.ABC):

    def __init__(self, stdscr: "curses.window") -> None:
        self.stdscr = stdscr
        self._running = True
        try:
            curses.curs_set(0)
        except Exception:
            pass

        try:
            self.stdscr.keypad(True)
        except Exception:
            pass

    def run(self) -> Optional[str]:
        try:
            self.on_enter()
            while self._running:
                try:
                    self.render()
                except Exception:
                    try:
                        self.stdscr.refresh()
                    except Exception:
                        pass

                try:
                    key = self.stdscr.getch()
                except Exception:
                    break

                try:
                    result = self.handle_key(key)
                except Exception:
                    result = None

                if result is not None:
                    return result
        finally:
            try:
                self.on_exit()
            except Exception:
                pass

        return None


    def on_enter(self) -> None:
        return None

    def on_exit(self) -> None:
        return None

    def stop(self) -> None:
        self._running = False

    def draw_centered(self, y: int, text: str, attr: int = curses.A_NORMAL) -> None:
        max_y, max_x = self.stdscr.getmaxyx()
        x = max(0, (max_x - len(text)) // 2)
        try:
            self.stdscr.addnstr(y, x, text, max_x - x - 1, attr)
        except curses.error:
            pass

    def draw_block_centered(self, start_y: int, lines: Sequence[str], attr: int = curses.A_NORMAL) -> None:
        for i, line in enumerate(lines):
            self.draw_centered(start_y + i, line, attr)

    def init_color_pair(self, pair_number: int, fg: int, bg: int) -> None:
        if not curses.has_colors():
            return
        try:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(pair_number, fg, bg)
        except Exception:
            pass

    def color_pair(self, pair_number: int) -> int:
        if not curses.has_colors():
            return curses.A_NORMAL
        try:
            return curses.color_pair(pair_number)
        except Exception:
            return curses.A_NORMAL


    @abc.abstractmethod
    def render(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def handle_key(self, key: int) -> Optional[str]:
        raise NotImplementedError
