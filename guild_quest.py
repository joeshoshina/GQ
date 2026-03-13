from typing import Generator, Optional
import os

from ui import (
    ScreenManager,
    ScreenEvent,
    ScreenState,
    MenuState,
    MenuOption,
    RegistrationState,
    LoginState,
    SettingsState,
    CharacterSelectState,
    CharacterCreateState,
    AdventureState,
    AdventureResultState,
)

from persistence import get_default_repository, UserAlreadyExists
from character_repository import (
    get_default_character_repository,
    CharacterAlreadyExists,
)
from guild_quest_subsystem.user import Username, Password, User, Score
from guild_quest_subsystem.enums import CharacterClass

_BASE_DIR = os.path.dirname(__file__)
_DATA_FILE = os.path.join(_BASE_DIR, "data", "users.json")
_CHAR_FILE = os.path.join(_BASE_DIR, "data", "characters.json")
_repo = get_default_repository(path=_DATA_FILE)
_char_repo = get_default_character_repository(path=_CHAR_FILE)

_PHASE_TITLE    = "title"
_PHASE_P1_LOGIN = "p1_login"
_PHASE_P1_CHAR  = "p1_char"
_PHASE_P2_LOGIN = "p2_login"
_PHASE_P2_CHAR  = "p2_char"
_PHASE_ADV_MENU = "adv_menu"
_PHASE_PLAYING  = "playing"
_PHASE_RESULT   = "result"
_TITLE_STATE = MenuState(
    screen_id="title",
    title="GuildQuest",
    subtitle="Mini-Adventure Environment",
    options=[
        MenuOption(id="Login", label="Login"),
        MenuOption(id="Register", label="Register"),
        MenuOption(id="Settings", label="Settings"),
        MenuOption(id="Exit", label="Exit"),
    ],
)

def _login_state(player_num: int, error: str = "", values: dict = None) -> LoginState:
    return LoginState(
        screen_id="Login",
        title=f"Player {player_num}  ·  Login",
        values=values or {"username": "", "password": ""},
        error=error or None,
    )


def _char_select_state(
    player_num: int, user_id: str, username: str, chars
) -> CharacterSelectState:
    return CharacterSelectState(
        screen_id="CharacterSelect",
        user_id=user_id,
        username=username,
        characters=chars,
        subtitle=f"Player {player_num}  ·  Choose Your Character",
        help_text="Use Arrows to navigate - Enter to select - Esc to go back",
    )


def _adventure_menu_state(p1: dict, p2: dict) -> MenuState:
    return MenuState(
        screen_id="adventures",
        title="Choose Adventure",
        subtitle=f"{p1['username']} (P1)  vs  {p2['username']} (P2)",
        options=[
            MenuOption(id="Relic Hunt",     label="Relic Hunt"),
            MenuOption(id="Escort Mission", label="Escort Mission", enabled=False),
            MenuOption(id="Back",           label="Back to Main Menu"),
        ],
    )


def _adventure_state(p1: dict, p2: dict, session_id: int) -> AdventureState:
    return AdventureState(
        screen_id="RelicHunt",
        adventure_name="Relic Hunt",
        game_state={
            "player1_name":  p1.get("char_name",  p1["username"]),
            "player1_class": p1.get("char_class", "Warrior"),
            "player1_level": p1.get("char_level", 1),
            "player2_name":  p2.get("char_name",  p2["username"]),
            "player2_class": p2.get("char_class", "Warrior"),
            "player2_level": p2.get("char_level", 1),
        },
        session_id=session_id,
    )


def _result_state(game_state: dict, p1: dict, p2: dict) -> AdventureResultState:
    result_text = str(game_state.get("result", "Adventure Complete!"))

    players = list(game_state.get("players", []))
    stats_lines = []
    for i, pl in enumerate(players):
        pname  = pl.get("name",   f"Player {i + 1}")
        relics = pl.get("relics", 0)
        stats_lines.append(f"P{i + 1}  {pname}:  {relics} relic(s) collected")

    return AdventureResultState(
        screen_id="AdventureResult",
        adventure_name="Relic Hunt",
        result_text=result_text,
        stats_lines=tuple(stats_lines),
    )


def _attempt_login(username_raw: str, password_raw: str):
    """Returns (record_dict, error_string). record_dict is None on failure."""
    try:
        u = Username(username_raw)
        u.value = username_raw
        p = Password(password_raw)
    except (TypeError, ValueError) as exc:
        return None, str(exc)
    try:
        record = _repo.verify_password(u, p)
    except Exception as exc:
        return None, str(exc)
    if record is None:
        return None, "Invalid username or password."
    return record, None



def app_flow() -> Generator[ScreenState, ScreenEvent, None]: 
    phase      = _PHASE_TITLE
    p1: dict   = {}   # {user_id, username, char_name, char_class, char_level}
    p2: dict   = {}
    session_id = 0

    event = yield _TITLE_STATE

    while True:
        if event is None:
            event = yield _TITLE_STATE
            continue

        name = event.name

        # ════════════════════════════════════════════════════════════════════
        # REGISTRATION
        # ════════════════════════════════════════════════════════════════════
        if name == "register.back":
            phase = _PHASE_TITLE
            event = yield _TITLE_STATE
            continue

        if name == "register.submit":
            username_raw = event.payload.get("username", "")
            password_raw = event.payload.get("password", "")
            try:
                u = Username(username_raw)
                u.value = username_raw
                p = Password(password_raw)
            except (TypeError, ValueError) as exc:
                event = yield RegistrationState(
                    screen_id="Register",
                    values={"username": username_raw, "password": password_raw,
                            "confirm_password": ""},
                    error=str(exc),
                )
                continue
            try:
                _repo.save_user(u, p)
            except UserAlreadyExists:
                event = yield RegistrationState(
                    screen_id="Register",
                    values={"username": username_raw, "password": password_raw,
                            "confirm_password": ""},
                    error=f"User '{u.value}' already exists.",
                )
                continue
            except Exception as exc:
                event = yield RegistrationState(
                    screen_id="Register",
                    values={"username": username_raw, "password": password_raw,
                            "confirm_password": ""},
                    error=str(exc),
                )
                continue
            phase = _PHASE_TITLE
            event = yield _TITLE_STATE
            continue

        if name in ("settings.back", "settings.save"):
            event = yield _TITLE_STATE
            continue
        if name == "login.back":
            phase = _PHASE_TITLE
            p1.clear()
            p2.clear()
            event = yield _TITLE_STATE
            continue

        if name == "login.submit":
            username_raw = event.payload.get("username", "")
            password_raw = event.payload.get("password", "")
            player_num   = 1 if phase == _PHASE_P1_LOGIN else 2
            record, err  = _attempt_login(username_raw, password_raw)

            if err:
                event = yield _login_state(
                    player_num,
                    error=err,
                    values={"username": username_raw, "password": password_raw},
                )
                continue

            uid      = record["id"]
            username = record["username"]
            chars    = _char_repo.get_characters_for_user(uid)

            if phase == _PHASE_P1_LOGIN:
                p1    = {"user_id": uid, "username": username}
                phase = _PHASE_P1_CHAR
                event = yield _char_select_state(1, uid, username, chars)
            else:
                p2    = {"user_id": uid, "username": username}
                phase = _PHASE_P2_CHAR
                event = yield _char_select_state(2, uid, username, chars)
            continue

        if name == "character_select.back":
            if phase == _PHASE_P1_CHAR:
                phase = _PHASE_TITLE
                p1.clear()
                event = yield _TITLE_STATE
            elif phase == _PHASE_P2_CHAR:
                phase = _PHASE_P2_LOGIN
                p2.clear()
                event = yield _login_state(2)
            else:
                event = yield _TITLE_STATE
            continue

        if name == "character_select.new":
            user_id  = event.payload.get("user_id",  "")
            username = event.payload.get("username", "")
            event    = yield CharacterCreateState(
                screen_id="CharacterCreate",
                user_id=user_id,
                username=username,
            )
            continue

        if name == "character_select.choose":
            char_name  = event.payload.get("character_name",  "")
            char_class = event.payload.get("character_class", "Warrior")
            char_level = int(event.payload.get("character_level", 1))

            if phase == _PHASE_P1_CHAR:
                p1.update({"char_name": char_name, "char_class": char_class,
                           "char_level": char_level})
                phase = _PHASE_P2_LOGIN
                event = yield _login_state(2)

            elif phase == _PHASE_P2_CHAR:
                p2.update({"char_name": char_name, "char_class": char_class,
                           "char_level": char_level})
                phase = _PHASE_ADV_MENU
                event = yield _adventure_menu_state(p1, p2)

            else:
                event = yield _TITLE_STATE
            continue

        if name == "character_create.back":
            user_id    = event.payload.get("user_id",  "")
            username   = event.payload.get("username", "")
            chars      = _char_repo.get_characters_for_user(user_id)
            player_num = 1 if phase == _PHASE_P1_CHAR else 2
            event      = yield _char_select_state(player_num, user_id, username, chars)
            continue

        if name == "character_create.submit":
            user_id   = event.payload.get("user_id",  "")
            username  = event.payload.get("username", "")
            char_name = event.payload.get("name",     "")
            class_val = event.payload.get("character_class", CharacterClass.WARRIOR.value)
            try:
                character_class = CharacterClass(class_val)
            except ValueError:
                character_class = CharacterClass.WARRIOR
            try:
                _char_repo.create_character(
                    user_id=user_id,
                    name=char_name,
                    character_class=character_class,
                )
            except CharacterAlreadyExists as exc:
                event = yield CharacterCreateState(
                    screen_id="CharacterCreate",
                    user_id=user_id, username=username, error=str(exc),
                )
                continue
            except Exception as exc:
                event = yield CharacterCreateState(
                    screen_id="CharacterCreate",
                    user_id=user_id, username=username, error=str(exc),
                )
                continue
            chars      = _char_repo.get_characters_for_user(user_id)
            player_num = 1 if phase == _PHASE_P1_CHAR else 2
            event      = yield _char_select_state(player_num, user_id, username, chars)
            continue
        if name == "menu.select":
            opt = event.payload.get("option_id", "")

            if opt == "Exit":
                return

            if opt == "Register":
                event = yield RegistrationState(screen_id="Register")
                continue

            if opt == "Settings":
                event = yield SettingsState(screen_id="Settings")
                continue

            if opt == "Login":
                phase = _PHASE_P1_LOGIN
                p1.clear()
                p2.clear()
                event = yield _login_state(1)
                continue

            if opt == "Relic Hunt" and phase == _PHASE_ADV_MENU:
                session_id += 1
                phase  = _PHASE_PLAYING
                event  = yield _adventure_state(p1, p2, session_id)
                continue

            if opt == "Back" and phase == _PHASE_ADV_MENU:
                phase = _PHASE_TITLE
                p1.clear()
                p2.clear()
                event = yield _TITLE_STATE
                continue

            event = yield _TITLE_STATE
            continue

        if name == "adventure.update":
            gs    = event.payload.get("game_state", {})
            event = yield AdventureState(
                screen_id="RelicHunt",
                adventure_name="Relic Hunt",
                game_state=gs,
                session_id=session_id,
            )
            continue

        if name == "adventure.complete":
            phase = _PHASE_RESULT
            gs    = event.payload.get("game_state", {})
            event = yield _result_state(gs, p1, p2)
            continue

        if name == "adventure.exit":
            phase = _PHASE_TITLE
            p1.clear()
            p2.clear()
            event = yield _TITLE_STATE
            continue
        if name == "adventure_result.select":
            opt = event.payload.get("option_id", "")
            if opt == "Play Again":
                session_id += 1
                phase = _PHASE_PLAYING
                event = yield _adventure_state(p1, p2, session_id)
            else:
                phase = _PHASE_TITLE
                p1.clear()
                p2.clear()
                event = yield _TITLE_STATE
            continue

        event = yield _TITLE_STATE



def main() -> None:
    ScreenManager().run(state_stream=app_flow())


if __name__ == "__main__":
    main()
