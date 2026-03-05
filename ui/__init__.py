import importlib
import sys
import curses
from typing import Callable, Dict, Generator, Optional

from .models import MenuOption, MenuState, ScreenEvent, ScreenState
from .registry import ScreenRegistry

_base_mod = importlib.import_module(".base_screen", __package__)
sys.modules.setdefault("base_screen", _base_mod)
_menu_mod = importlib.import_module(".menu_screen", __package__)
sys.modules.setdefault("menu_screen", _menu_mod)
_title_mod = importlib.import_module(".title_screen", __package__)
sys.modules.setdefault("title_screen", _title_mod)

BaseScreen = _base_mod.BaseScreen
MenuScreen = _menu_mod.MenuScreen
TitleScreen = _title_mod.TitleScreen


class ScreenManager:
    def __init__(
        self,
        registry: Optional[ScreenRegistry] = None,
        initial: str = "title",
    ) -> None:
        self._registry = registry or self._default_registry()
        self._initial = initial
        self._screen_cache: Dict[str, BaseScreen] = {}

    def _default_registry(self) -> ScreenRegistry:
        registry = ScreenRegistry()
        registry.register("title", lambda stdscr: TitleScreen(stdscr))
        registry.register(
            "Login",
            lambda stdscr: MenuScreen(
                stdscr,
                menu_state=MenuState(
                    screen_id="Login",
                    title="Login",
                    subtitle="Not implemented",
                    options=[MenuOption(id="Back", label="Back")],
                ),
            ),
        )
        registry.register(
            "Register",
            lambda stdscr: MenuScreen(
                stdscr,
                menu_state=MenuState(
                    screen_id="Register",
                    title="Register",
                    subtitle="Not implemented",
                    options=[MenuOption(id="Back", label="Back")],
                ),
            ),
        )
        registry.register(
            "Settings",
            lambda stdscr: MenuScreen(
                stdscr,
                menu_state=MenuState(
                    screen_id="Settings",
                    title="Settings",
                    subtitle="Not implemented",
                    options=[MenuOption(id="Back", label="Back")],
                ),
            ),
        )
        return registry

    def register(self, screen_id: str, factory: Callable[["curses.window"], BaseScreen]) -> None:
        self._registry.register(screen_id, factory)

    def run(self, state_stream: Optional[Generator[ScreenState, ScreenEvent, None]] = None) -> None:
        try:
            if state_stream is None:
                curses.wrapper(self._main_legacy)
            else:
                curses.wrapper(lambda stdscr: self._main_state(stdscr, state_stream))
        except Exception:
            pass

    def _get_screen(self, stdscr: "curses.window", screen_id: str) -> Optional[BaseScreen]:
        screen = self._screen_cache.get(screen_id)
        if screen is not None:
            return screen
        factory = self._registry.get(screen_id)
        if factory is None:
            return None
        screen = factory(stdscr)
        self._screen_cache[screen_id] = screen
        return screen

    def _main_state(
        self,
        stdscr: "curses.window",
        state_stream: Generator[ScreenState, ScreenEvent, None],
    ) -> None:
        try:
            state = next(state_stream)
        except StopIteration:
            return

        while True:
            screen = self._get_screen(stdscr, state.screen_id)
            if screen is None:
                break
            screen.set_state(state)
            while True:
                try:
                    screen.render()
                except Exception:
                    try:
                        stdscr.refresh()
                    except Exception:
                        pass
                try:
                    key = stdscr.getch()
                except Exception:
                    return
                try:
                    event = screen.handle_key(key)
                except Exception:
                    event = None

                if event is None:
                    continue

                try:
                    state = state_stream.send(event)
                except StopIteration:
                    return
                break

    def _main_legacy(self, stdscr: "curses.window") -> None:
        stack: list[BaseScreen] = []
        screen = self._get_screen(stdscr, self._initial)
        if screen is None:
            return
        stack.append(screen)

        while stack:
            current = stack[-1]
            try:
                result = current.run()
            except Exception:
                result = None

            if result is None:
                break

            cmd = str(result)

            if cmd in ("Back", "back"):
                stack.pop()
                if not stack:
                    break
                continue

            if cmd.lower() in ("quit", "exit"):
                break

            next_screen = self._get_screen(stdscr, cmd)
            if next_screen:
                stack.append(next_screen)
                continue

            break


__all__ = [
    "ScreenManager",
    "ScreenRegistry",
    "ScreenEvent",
    "ScreenState",
    "MenuOption",
    "MenuState",
    "BaseScreen",
    "MenuScreen",
    "TitleScreen",
]
