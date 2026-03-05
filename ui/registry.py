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
