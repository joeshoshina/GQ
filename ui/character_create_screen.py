import curses
from typing import List, Optional

from .base_screen import BaseScreen
from .models import CharacterCreateState, ScreenEvent

from guild_quest_subsystem.enums import CharacterClass

_MAX_NAME_LEN = 24
_CLASSES: List[CharacterClass] = list(CharacterClass)


class CharacterCreateScreen(BaseScreen):
    def __init__(self, stdscr: "curses.window") -> None:
        super().__init__(stdscr)
        self._state: CharacterCreateState = CharacterCreateState(
            screen_id="CharacterCreate",
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
                curses.init_pair(4, curses.COLOR_GREEN, -1)
                curses.init_pair(5, curses.COLOR_CYAN, -1)
                curses.init_pair(6, curses.COLOR_YELLOW, -1)
            except Exception:
                pass

    def set_state(self, state: CharacterCreateState) -> None:
        super().set_state(state)
        self._state = state
        try:
            curses.curs_set(1 if state.step == "name" else 0)
        except Exception:
            pass

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
        if self._state.step == "class":
            self._render_class_step()
        else:
            self._render_name_step()

    def _render_class_step(self) -> None:
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        s = self._state
        top_y = max(1, max_y // 8)

        self._draw_centered(top_y, "Create Character", curses.A_BOLD)
        self._draw_centered(top_y + 1, "Step 1 of 2 — Choose a Class", curses.A_DIM)

        idx = max(0, min(s.selected_class_index, len(_CLASSES) - 1))
        menu_top = top_y + 3

        for i, cls in enumerate(_CLASSES):
            y = menu_top + i * 2
            if i == idx:
                attr = curses.A_REVERSE | curses.A_BOLD
            else:
                attr = curses.A_NORMAL
            self._draw_centered(y, cls.value, attr)

        # Description panel for highlighted class
        desc_y = menu_top + len(_CLASSES) * 2 + 1
        selected_cls = _CLASSES[idx]
        desc_attr = curses.color_pair(5) if curses.has_colors() else curses.A_DIM
        self._draw_centered(desc_y, selected_cls.description(), desc_attr)

        if s.error:
            self._draw_centered(
                desc_y + 2,
                s.error,
                curses.color_pair(3) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD,
            )

        self._draw_centered(max_y - 2, s.help_text, curses.A_DIM)
        self.stdscr.refresh()

    def _render_name_step(self) -> None:
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        s = self._state
        top_y = max(1, max_y // 6)

        selected_cls = _CLASSES[max(0, min(s.selected_class_index, len(_CLASSES) - 1))]

        self._draw_centered(top_y, "Create Character", curses.A_BOLD)
        self._draw_centered(top_y + 1, "Step 2 of 2 — Name Your Character", curses.A_DIM)

        cls_label = f"Class: {selected_cls.value}"
        cls_attr = curses.color_pair(5) if curses.has_colors() else curses.A_NORMAL
        self._draw_centered(top_y + 3, cls_label, cls_attr)

        field_y = top_y + 5
        label = "Character Name:"
        display = s.name_value if s.name_value else ""
        field_text = f"{label:<20} {display:<{_MAX_NAME_LEN}}"
        self._draw_centered(field_y, field_text, curses.A_REVERSE | curses.A_BOLD)

        counter_text = f"{len(s.name_value)}/{_MAX_NAME_LEN}"
        self._draw_centered(field_y + 1, counter_text, curses.A_DIM)

        if s.error:
            self._draw_centered(
                field_y + 3,
                s.error,
                curses.color_pair(3) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD,
            )
        elif s.name_value.strip():
            preview = f'Will be created as: "{s.name_value.strip()}"  Level 1  {selected_cls.value}'
            self._draw_centered(
                field_y + 3,
                preview,
                curses.color_pair(4) if curses.has_colors() else curses.A_DIM,
            )

        self._draw_centered(max_y - 2, s.help_text, curses.A_DIM)
        self.stdscr.refresh()

    def handle_key(self, key: int) -> Optional[ScreenEvent]:
        if self._state.step == "class":
            return self._handle_class_step(key)
        return self._handle_name_step(key)

    def _handle_class_step(self, key: int) -> Optional[ScreenEvent]:
        s = self._state

        if key == 27:  # Esc → back to character select
            return ScreenEvent(name="character_create.back", payload={"user_id": s.user_id, "username": s.username})

        if key == curses.KEY_UP:
            new_idx = (s.selected_class_index - 1) % len(_CLASSES)
            self._state = self._make_state(s, selected_class_index=new_idx, error=None)
            return None

        if key == curses.KEY_DOWN:
            new_idx = (s.selected_class_index + 1) % len(_CLASSES)
            self._state = self._make_state(s, selected_class_index=new_idx, error=None)
            return None

        if key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            # Advance to name step
            self._state = self._make_state(s, step="name", error=None)
            try:
                curses.curs_set(1)
            except Exception:
                pass
            return None

        return None

    def _handle_name_step(self, key: int) -> Optional[ScreenEvent]:
        s = self._state

        if key == 27:  # Esc → back to class step
            self._state = self._make_state(s, step="class", name_value="", error=None)
            try:
                curses.curs_set(0)
            except Exception:
                pass
            return None

        if key in (curses.KEY_BACKSPACE, 127, 8):
            self._state = self._make_state(s, name_value=s.name_value[:-1], error=None)
            return None

        if key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            return self._submit()

        if 32 <= key <= 126:
            if len(s.name_value) < _MAX_NAME_LEN:
                self._state = self._make_state(
                    s,
                    name_value=s.name_value + chr(key),
                    error=None,
                )
            return None

        return None

    def _submit(self) -> Optional[ScreenEvent]:
        s = self._state
        name = s.name_value.strip()

        if not name:
            self._state = self._make_state(s, error="Character name cannot be empty.")
            return None

        if len(name) < 2:
            self._state = self._make_state(s, error="Name must be at least 2 characters.")
            return None

        selected_cls = _CLASSES[max(0, min(s.selected_class_index, len(_CLASSES) - 1))]

        return ScreenEvent(
            name="character_create.submit",
            payload={
                "user_id": s.user_id,
                "username": s.username,
                "name": name,
                "character_class": selected_cls.value,
            },
        )

    def _make_state(
        self,
        s: CharacterCreateState,
        selected_class_index: Optional[int] = None,
        name_value: Optional[str] = None,
        step: Optional[str] = None,
        error: Optional[str] = None,
    ) -> CharacterCreateState:
        return CharacterCreateState(
            screen_id=s.screen_id,
            user_id=s.user_id,
            username=s.username,
            selected_class_index=selected_class_index if selected_class_index is not None else s.selected_class_index,
            name_value=name_value if name_value is not None else s.name_value,
            step=step if step is not None else s.step,
            error=error,
            help_text=s.help_text,
        )
