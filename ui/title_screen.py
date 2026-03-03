from typing import Tuple

from .menu_screen import MenuScreen
import curses

_MENU_OPTIONS: Tuple[str, ...] = ("Login", "Settings", "Register")


class TitleScreen(MenuScreen):
    def __init__(self, stdscr: "curses.window", options: Tuple[str, ...] = _MENU_OPTIONS) -> None:
        super().__init__(
            stdscr,
            options=options,
            title="GuildQuest",
            subtitle="Mini-Adventure Environment",
            highlight_pair=1,
        )
