"""
GuildQuest UI System with Event-Driven State Machine.

This module orchestrates the UI application with an event-driven state machine:
- ScreenManager: Central coordinator managing screen lifecycle and state transitions
- app_flow(): Generator-based state machine that yields states and receives ScreenEvent objects
- Input handling: Keyboard events → screen.handle_key() → ScreenEvent → state change

Key responsibilities:
- Screen factory instantiation via ScreenRegistry (Factory Pattern)
- Event-driven state transitions via generator protocol (yield/send)
- Curses event loop integration (blocking getkey() calls)
"""
import importlib
import sys
import curses
import queue
from typing import Callable, Dict, Generator, Optional

from .models import (
    AdventureResultState,
    AdventureState,
    MenuOption,
    MenuState,
    RegistrationState,
    LoginState,
    SettingsState,
    ScreenEvent,
    ScreenState,
    CharacterSelectState,
    CharacterCreateState,
)
from .registry import ScreenRegistry, build_default_registry

_base_mod = importlib.import_module(".base_screen", __package__)
sys.modules.setdefault("base_screen", _base_mod)
_menu_mod = importlib.import_module(".menu_screen", __package__)
sys.modules.setdefault("menu_screen", _menu_mod)
_title_mod = importlib.import_module(".title_screen", __package__)
sys.modules.setdefault("title_screen", _title_mod)
_login_mod = importlib.import_module(".login_screen", __package__)
sys.modules.setdefault("login_screen", _login_mod)
_reg_mod = importlib.import_module(".registration_screen", __package__)
sys.modules.setdefault("registration_screen", _reg_mod)
_settings_mod = importlib.import_module(".settings_screen", __package__)
sys.modules.setdefault("settings_screen", _settings_mod)
_char_select_mod = importlib.import_module(".character_select_screen", __package__)
sys.modules.setdefault("character_select_screen", _char_select_mod)
_char_create_mod = importlib.import_module(".character_create_screen", __package__)
sys.modules.setdefault("character_create_screen", _char_create_mod)

BaseScreen = _base_mod.BaseScreen
MenuScreen = _menu_mod.MenuScreen
TitleScreen = _title_mod.TitleScreen
LoginScreen = _login_mod.LoginScreen
RegistrationScreen = _reg_mod.RegistrationScreen
SettingsScreen = _settings_mod.SettingsScreen
CharacterSelectScreen = _char_select_mod.CharacterSelectScreen
CharacterCreateScreen = _char_create_mod.CharacterCreateScreen


class ScreenManager:
    def __init__(self, registry: Optional[ScreenRegistry] = None) -> None:
        self._registry = registry or build_default_registry()
        self._screen_cache: Dict[str, BaseScreen] = {}
        self._external_queue = queue.Queue()



    def register(self, screen_id: str, factory: Callable[["curses.window"], BaseScreen]) -> None:
        self._registry.register(screen_id, factory)

    def push_event(self, event):
        self._external_queue.put(event)

    def run(self, state_stream: Generator[ScreenState, ScreenEvent, None]) -> None:
        curses.wrapper(lambda stdscr: self._main(stdscr, state_stream))

    def _get_screen(self, stdscr: "curses.window", screen_id: str) -> Optional[BaseScreen]:
        screen = self._screen_cache.get(screen_id)
        if screen is not None:
            return screen
        factory = self._registry.get(screen_id)
        if factory is None:
            return None
        screen = factory(stdscr)
        self._screen_cache[screen_id] = screen
        try:
            screen.on_enter()
        except Exception:
            pass
        return screen

    def _main(self, stdscr: "curses.window", state_stream: Generator[ScreenState, ScreenEvent, None]) -> None:
        try:
            curses.start_color()
            curses.use_default_colors()
            stdscr.bkgd(' ', curses.color_pair(0))
        except Exception:
            pass
        try:
            state = next(state_stream)
        except StopIteration: # nothing to render
            return

        while True:
            screen = self._get_screen(stdscr, state.screen_id)
            if screen is None:
                break
            try:
                screen.set_state(state)
            except Exception:
                pass

            while True:
                try:
                    screen.render()
                except Exception:
                    try:
                        stdscr.refresh()
                    except Exception:
                        pass

                try:
                    ext_event = self._external_queue.get_nowait()
                except Exception:
                    ext_event = None

                if ext_event is not None:
                    try:
                        state = state_stream.send(ext_event)
                    except StopIteration:
                        return
                    break

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
