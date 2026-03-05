from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence


@dataclass(frozen=True)
class ScreenEvent:
    name: str
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class ScreenState:
    screen_id: str


@dataclass(frozen=True)
class MenuOption:
    id: str
    label: str
    enabled: bool = True


@dataclass
class MenuState(ScreenState):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    options: Sequence[MenuOption] = field(default_factory=tuple)
    selected_index: int = 0
    help_text: str = "Use Arrows to navigate — Enter to select"

@dataclass
class RegistrationState(ScreenState):
    fields: Sequence[str] = field(default_factory=lambda: ["username", "password", "confirm_password"])
    values: dict = field(default_factory=dict)
    active_field: int = 0
    error: Optional[str] = None
    help_text: str = "Tab/Arrows to move — Enter to submit — Esc to go back"
