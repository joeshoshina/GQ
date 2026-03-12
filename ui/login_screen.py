import curses
from typing import Optional

from .base_screen import BaseScreen
from .models import LoginState, ScreenEvent


class LoginScreen(BaseScreen):
    def __init__(self, stdscr: "curses.window") -> None:
        super().__init__(stdscr)
        self._state: LoginState = LoginState(
            screen_id="Login",
            fields=["username", "password"],
            values={"username": "", "password": ""},
        )

    def on_enter(self) -> None:
        try:
            curses.curs_set(1)
        except Exception:
            pass
        try:
            self.stdscr.keypad(True)
        except Exception:
            pass
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, -1, -1)
            curses.init_pair(2, -1, -1)
            curses.init_pair(3, curses.COLOR_RED, -1)

    def set_state(self, state: LoginState) -> None:
        super().set_state(state)
        self._state = state

    def _draw_centered(self, y: int, text: str, attr: int = curses.A_NORMAL) -> None:
        max_y, max_x = self.stdscr.getmaxyx()
        if y < 0 or y >= max_y:
            return
        x = max(0, (max_x - len(text)) // 2)
        try:
            self.stdscr.addnstr(y, x, text, max_x - x - 1, attr)
        except curses.error:
            pass

    def render(self) -> None:
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        s = self._state
        top_y = max(1, max_y // 6)

        self._draw_centered(top_y, "Login", curses.A_BOLD)

        field_top = top_y + 3
        for i, field_name in enumerate(s.fields):
            y = field_top + i * 3
            label = field_name.replace("_", " ").title() + ":"
            value = s.values.get(field_name, "")
            display = "*" * len(value) if "password" in field_name else value

            attr = curses.A_BOLD | curses.A_REVERSE if i == s.active_field else curses.A_NORMAL
            self._draw_centered(y, f"{label:<20} {display:<30}", attr)

        if s.error:
            self._draw_centered(
                field_top + len(s.fields) * 3 + 1,
                s.error,
                curses.color_pair(3) | curses.A_BOLD,
            )

        self._draw_centered(max_y - 2, s.help_text, curses.A_DIM)
        self.stdscr.refresh()

    def _make_state(
        self,
        s: LoginState,
        active_field: int = None,
        values: dict = None,
        error: str = None,
    ) -> LoginState:
        return LoginState(
            screen_id=s.screen_id,
            fields=s.fields,
            values=values if values is not None else s.values,
            active_field=active_field if active_field is not None else s.active_field,
            error=error,
            help_text=s.help_text,
        )

    def handle_key(self, key: int) -> Optional[object]:
        s = self._state

        if key == 27:  # Esc → go back
            return ScreenEvent(name="login.back", payload={})

        if key in (curses.KEY_DOWN, ord("\t")):
            self._state = self._make_state(
                s, active_field=(s.active_field + 1) % len(s.fields)
            )
            return None

        if key == curses.KEY_UP:
            self._state = self._make_state(
                s, active_field=(s.active_field - 1) % len(s.fields)
            )
            return None

        if key in (curses.KEY_BACKSPACE, 127, 8):
            field = s.fields[s.active_field]
            new_values = dict(s.values)
            new_values[field] = s.values.get(field, "")[:-1]
            self._state = self._make_state(s, values=new_values)
            return None

        if key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            return self._submit()

        if 32 <= key <= 126:
            field = s.fields[s.active_field]
            new_values = dict(s.values)
            new_values[field] = s.values.get(field, "") + chr(key)
            self._state = self._make_state(s, values=new_values)
            return None

        return None

    def _submit(self) -> Optional[ScreenEvent]:
        s = self._state
        username = s.values.get("username", "").strip()
        password = s.values.get("password", "")

        if not username:
            self._state = self._make_state(s, error="Username cannot be empty.")
            return None
        if not password:
            self._state = self._make_state(s, error="Password cannot be empty.")
            return None

        return ScreenEvent(
            name="login.submit",
            payload={"username": username, "password": password},
        )
