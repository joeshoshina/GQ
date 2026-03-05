from typing import Optional, Tuple

from .menu_screen import MenuScreen
from .models import MenuOption, MenuState

_MENU_OPTIONS: Tuple[str, ...] = ("Login", "Settings", "Register", "Exit")


class TitleScreen(MenuScreen):
    def __init__(
        self,
        stdscr,
        options: Tuple[str, ...] = _MENU_OPTIONS,
        menu_state: Optional[MenuState] = None,
        emit_events: bool = False,
    ) -> None:
        if menu_state is None:
            menu_state = MenuState(
                screen_id="title",
                title="GuildQuest",
                subtitle="Mini-Adventure Environment",
                options=[MenuOption(id=opt, label=opt) for opt in options],
                selected_index=0,
            )
        super().__init__(
            stdscr,
            menu_state=menu_state,
            highlight_pair=1,
            emit_events=emit_events,
        )
