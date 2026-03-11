import curses
from typing import Callable, Dict, Optional

from .base_screen import BaseScreen
from .settings_screen import SettingsScreen

ScreenFactory = Callable[["curses.window"], BaseScreen]


class ScreenRegistry:
    def __init__(self) -> None:
        self._factories: Dict[str, ScreenFactory] = {}

    def register(self, screen_id: str, factory: ScreenFactory) -> None:
        self._factories[screen_id] = factory

    def unregister(self, screen_id: str) -> None:
        self._factories.pop(screen_id, None)

    def get(self, screen_id: str) -> Optional[ScreenFactory]:
        return self._factories.get(screen_id)

    def all(self) -> Dict[str, ScreenFactory]:
        return dict(self._factories)

def build_default_registry() -> ScreenRegistry:
    from .adventure_result_screen import AdventureResultScreen
    from .adventure_screen import AdventureScreen
    from .menu_screen import MenuScreen
    from .models import MenuOption, MenuState
    from .registration_screen import RegistrationScreen
    from .login_screen import LoginScreen
    from .title_screen import TitleScreen
    from mini_adventures.relic_hunt import RelicRaceAdventure
    from profile import PlayerProfile

    registry = ScreenRegistry()
    registry.register("title", lambda stdscr: TitleScreen(stdscr, emit_events=True))
    registry.register("Login", lambda stdscr: LoginScreen(stdscr))
    registry.register("Register", lambda stdscr: RegistrationScreen(stdscr))
    registry.register("Settings", lambda stdscr: SettingsScreen(stdscr))
    registry.register(
        "adventure.relic_hunt",
        lambda stdscr: AdventureScreen(
            stdscr,
            RelicRaceAdventure(
                PlayerProfile("Player 1"),
                PlayerProfile("Player 2"),
            ),
        ),
    )
    registry.register("adventure.result", lambda stdscr: AdventureResultScreen(stdscr))
    return registry
