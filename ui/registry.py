"""
Screen Factory Pattern Implementation.

This module implements the Factory Pattern for screen creation, allowing lazy instantiation
of UI screens on-demand with dependency injection.

Key components:
- ScreenFactory: Type alias for factory functions (callable that creates BaseScreen instances)
- ScreenRegistry: Maps screen IDs to factory functions; call registry.get(id) to retrieve factory
- build_default_registry(): Initializes registry with all available screens
"""
import curses
from typing import Callable, Dict, Optional

from .base_screen import BaseScreen

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
    from .relic_hunt_screen import RelicHuntScreen
    from .character_create_screen import CharacterCreateScreen
    from .character_select_screen import CharacterSelectScreen
    from .login_screen import LoginScreen
    from .menu_screen import MenuScreen
    from .models import MenuState
    from .registration_screen import RegistrationScreen
    from .settings_screen import SettingsScreen
    from .title_screen import TitleScreen

    registry = ScreenRegistry()
    registry.register("title", lambda stdscr: TitleScreen(stdscr, emit_events=True))
    registry.register(
        "home",
        lambda stdscr: MenuScreen(
            stdscr,
            emit_events=True,
            menu_state=MenuState(screen_id="home"),
        ),
    )
    registry.register(
        "adventures",
        lambda stdscr: MenuScreen(
            stdscr,
            emit_events=True,
            menu_state=MenuState(screen_id="adventures"),
        ),
    )
    registry.register("Login", lambda stdscr: LoginScreen(stdscr))
    registry.register("Register", lambda stdscr: RegistrationScreen(stdscr))
    registry.register("Settings", lambda stdscr: SettingsScreen(stdscr))
    registry.register("CharacterSelect", lambda stdscr: CharacterSelectScreen(stdscr))
    registry.register("CharacterCreate", lambda stdscr: CharacterCreateScreen(stdscr))
    registry.register("RelicHunt",       lambda stdscr: RelicHuntScreen(stdscr))
    registry.register("AdventureResult", lambda stdscr: AdventureResultScreen(stdscr))
    return registry
