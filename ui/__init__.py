import importlib
import sys
import curses
from typing import Callable, Dict, Optional

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
        screens: Optional[Dict[str, Callable[["curses.window"], BaseScreen]]] = None,
        initial: str = "title",
    ) -> None:
        self._screens = screens or self._default_screens()
        self._initial = initial

    def _default_screens(self) -> Dict[str, Callable[["curses.window"], BaseScreen]]:
        return {
            "title": lambda stdscr: TitleScreen(stdscr),
            "Login": lambda stdscr: MenuScreen(
                stdscr,
                options=("Back",),
                title="Login",
                subtitle="Not implemented",
            ),
            "Register": lambda stdscr: MenuScreen(
                stdscr,
                options=("Back",),
                title="Register",
                subtitle="Not implemented",
            ),
            "Settings": lambda stdscr: MenuScreen(
                stdscr,
                options=("Back",),
                title="Settings",
                subtitle="Not implemented",
            ),
        }

    def run(self) -> None:
        import curses

        try:
            curses.wrapper(self._main)
        except Exception:
            pass

    def _main(self, stdscr: "curses.window") -> None:
        stack: list[BaseScreen] = []
        factory = self._screens.get(self._initial)
        if factory is None:
            return
        stack.append(factory(stdscr))

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

            factory = self._screens.get(cmd)
            if factory:
                stack.append(factory(stdscr))
                continue

            break

__all__ = ["ScreenManager", "BaseScreen", "MenuScreen", "TitleScreen"]
