import curses
from typing import Optional

from .base_screen import BaseScreen
from .models import CharacterSelectState, ScreenEvent
from settings import Settings


class CharacterSelectScreen(BaseScreen):
    def __init__(self, stdscr: "curses.window") -> None:
        super().__init__(stdscr)
        self._state: CharacterSelectState = CharacterSelectState(
            screen_id="CharacterSelect",
        )

    def on_enter(self) -> None:
        try:
            curses.curs_set(0)
        except Exception:
            pass
        try:
            self.stdscr.keypad(True)
        except Exception:
            pass
        if curses.has_colors():
            try:
                curses.start_color()
                curses.use_default_colors()
                curses.init_pair(3, curses.COLOR_RED, -1)
                curses.init_pair(4, curses.COLOR_YELLOW, -1)
            except Exception:
                pass

    def set_state(self, state: CharacterSelectState) -> None:
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

    def _build_options(self):
        options = []
        for char in self._state.characters:
            label = f"{char.name}  -  {char.character_class.value}  (Level {char.level})"
            options.append((label, False))
        options.append(("+ New Character", True))
        return options

    def render(self) -> None:
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        s = self._state
        top_y = max(1, max_y // 6)

        self._draw_centered(top_y, s.subtitle, curses.A_BOLD)
        self._draw_centered(top_y + 1, f"Welcome, {s.username}", curses.A_DIM)

        try:
            formatted_score = Settings.get_instance().format_score(s.score)
        except Exception:
            formatted_score = str(s.score)
        score_attr = curses.color_pair(4) if curses.has_colors() else curses.A_NORMAL
        self._draw_centered(top_y + 2, f"Score: {formatted_score}", score_attr)

        options = self._build_options()
        if not options:
            self._draw_centered(max_y // 2, "No options available.", curses.A_DIM)
            self.stdscr.refresh()
            return

        idx = max(0, min(s.selected_index, len(options) - 1))
        menu_top = max(top_y + 5, max_y // 2 - len(options))

        for i, (label, is_new) in enumerate(options):
            y = menu_top + i * 2
            if i == idx:
                attr = curses.A_REVERSE | curses.A_BOLD
            elif is_new:
                attr = curses.color_pair(4) if curses.has_colors() else curses.A_NORMAL
            else:
                attr = curses.A_NORMAL
            self._draw_centered(y, label, attr)

        if s.error:
            error_y = menu_top + len(options) * 2 + 1
            self._draw_centered(
                error_y,
                s.error,
                curses.color_pair(3) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD,
            )

        self._draw_centered(max_y - 2, s.help_text, curses.A_DIM)
        self.stdscr.refresh()

    def handle_key(self, key: int) -> Optional[ScreenEvent]:
        s = self._state
        options = self._build_options()
        num_options = len(options)

        if key == 27:  # Esc → log out / back to title
            return ScreenEvent(name="character_select.back", payload={})

        if key == curses.KEY_UP:
            new_idx = (s.selected_index - 1) % num_options
            self._state = self._make_state(s, selected_index=new_idx)
            return None

        if key == curses.KEY_DOWN:
            new_idx = (s.selected_index + 1) % num_options
            self._state = self._make_state(s, selected_index=new_idx)
            return None

        if key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            idx = max(0, min(s.selected_index, num_options - 1))
            _label, is_new = options[idx]

            if is_new:
                return ScreenEvent(
                    name="character_select.new",
                    payload={"user_id": s.user_id, "username": s.username},
                )

            # Existing character selected
            char = s.characters[idx]
            return ScreenEvent(
                name="character_select.choose",
                payload={
                    "user_id": s.user_id,
                    "username": s.username,
                    "character_id": char.character_id,
                    "character_name": char.name,
                    "character_level": char.level,
                },
            )

        return None

    def _make_state(
        self,
        s: CharacterSelectState,
        selected_index: int = None,
        error: Optional[str] = None,
    ) -> CharacterSelectState:
        return CharacterSelectState(
            screen_id=s.screen_id,
            user_id=s.user_id,
            username=s.username,
            characters=s.characters,
            selected_index=selected_index if selected_index is not None else s.selected_index,
            error=error,
            subtitle=s.subtitle,
            help_text=s.help_text,
            score=s.score,
        )
