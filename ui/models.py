"""
UI State Models and Event Definitions.

This module defines immutable state objects for the UI system, including:
 - ScreenState: Base class for all screen states (mutable subclasses)
 - ScreenEvent: Immutable event objects that drive state transitions
 - AdventureState: Encapsulates game state from mini-adventures
 - AdventureResultState: Displays post-game results and replay options
"""

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
    help_text: str = "Use Arrows to navigate - Enter to select"

@dataclass
class RegistrationState(ScreenState):
    fields: Sequence[str] = field(default_factory=lambda: ["username", "password", "confirm_password"])
    values: dict = field(default_factory=dict)
    active_field: int = 0
    error: Optional[str] = None
    help_text: str = "Tab/Arrows to move - Enter to submit - Esc to go back"


@dataclass
class LoginState(ScreenState):
    fields: Sequence[str] = field(default_factory=lambda: ["username", "password"])
    values: dict = field(default_factory=dict)
    active_field: int = 0
    error: Optional[str] = None
    title: str = "Login" 
    help_text: str = "Tab/Arrows to move - Enter to submit - Esc to go back"


@dataclass
class SettingsState(ScreenState):
    score_display: str = "NUMERIC"
    error: Optional[str] = None
    help_text: str = "Left/Right to change - S to save - Esc to go back"


@dataclass
class AdventureState(ScreenState):
    adventure_name: str
    game_state: Mapping[str, Any] = field(default_factory=dict)
    help_text: str = "P1: WASD  P2: Arrow Keys - Esc to return"
    session_id: int = 0


@dataclass
class AdventureResultState(ScreenState):
    adventure_name: str
    result_text: str
    stats_lines: Sequence[str] = field(default_factory=tuple)
    options: Sequence[MenuOption] = field(
        default_factory=lambda: (
            MenuOption(id="Play Again", label="Play Again"),
            MenuOption(id="Back to Menu", label="Back to Menu"),
        )
    )
    selected_index: int = 0
    help_text: str = "Use Arrows to navigate - Enter to select"


@dataclass
class CharacterSelectState(ScreenState):
    user_id: str = ""
    username: str = ""
    characters: Sequence[Any] = field(default_factory=list)  # List[CharacterRecord]
    selected_index: int = 0
    error: Optional[str] = None
    subtitle: str = "Choose Your Character"
    help_text: str = "Use Arrows to navigate - Enter to select - Esc to log out"


@dataclass
class CharacterCreateState(ScreenState):
    user_id: str = ""
    username: str = ""
    selected_class_index: int = 0
    name_value: str = ""
    step: str = "class"
    error: Optional[str] = None
    help_text: str = "Use Arrows to navigate - Enter to confirm - Esc to go back"
