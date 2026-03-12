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


def _display_name(user: Optional[User]) -> str:
    if user is None or user.username is None:
        return "Adventurer"
    return str(user.username)


def _logged_in_menu_state(user: User) -> MenuState:
    username = _display_name(user)
    return MenuState(
        screen_id="home",
        title="GuildQuest",
        subtitle=f"Logged in as {username}",
        options=[
            MenuOption(id="Adventure", label="Adventure"),
            MenuOption(id="Settings", label="Settings"),
            MenuOption(id="Exit", label="Exit"),
        ],
    )


def _adventure_menu_state(user: User) -> MenuState:
    username = _display_name(user)
    return MenuState(
        screen_id="adventures",
        title="Adventures",
        subtitle=f"Logged in as {username}",
        options=[
            MenuOption(id="Relic Hunt", label="Relic Hunt"),
            MenuOption(id="Escort Mission", label="Escort Mission", enabled=False),
            MenuOption(id="Back", label="Back"),
        ],
    )


def _adventure_placeholder_state(user: User, adventure_name: str) -> MenuState:
    username = _display_name(user)
    return MenuState(
        screen_id="adventures",
        title=adventure_name,
        subtitle=f"Logged in as {username} - adventure UI wiring comes next",
        options=[MenuOption(id="Back", label="Back")],
    )


def app_flow() -> Generator[ScreenState, ScreenEvent, None]:
    current_user: Optional[User] = None
    event = yield _TITLE_STATE
    while True:
        if event is None:
            event = yield (_logged_in_menu_state(current_user) if current_user else _TITLE_STATE)
            continue

        # Menu navigation events
        if event.name == "menu.select":
            option_id = event.payload.get("option_id", "")
            if option_id == "Exit":
                if current_user is None:
                    return
                current_user = None
                event = yield _TITLE_STATE
                continue
            if option_id == "Register":
                event = yield RegistrationState(screen_id="Register")
                continue
            if option_id == "Login":
                event = yield LoginState(screen_id="Login")
                continue
            if option_id == "Adventure" and current_user is not None:
                event = yield _adventure_menu_state(current_user)
                continue
            if option_id == "Relic Hunt" and current_user is not None:
                event = yield _adventure_placeholder_state(current_user, "Relic Hunt")
                continue
            if option_id == "Escort Mission" and current_user is not None:
                event = yield _adventure_placeholder_state(current_user, "Escort Mission")
                continue
            if option_id == "Settings":
                event = yield SettingsState(screen_id="Settings")
                continue
            if option_id == "Back":
                event = yield (_logged_in_menu_state(current_user) if current_user else _TITLE_STATE)
                continue

        if event.name == "login.back":
            event = yield (_logged_in_menu_state(current_user) if current_user else _TITLE_STATE)
            continue

        if event.name == "login.submit":
            username_raw = event.payload.get("username", "")
            password_raw = event.payload.get("password", "")

            try:
                u = Username(username_raw)
                u.value = username_raw
                p = Password(password_raw)
            except (TypeError, ValueError) as exc:
                event = yield LoginState(
                    screen_id="Login",
                    values={"username": username_raw, "password": password_raw},
                    error=str(exc),
                )
                continue

            try:
                record = _repo.verify_password(u, p)
                if record is None:
                    event = yield LoginState(
                        screen_id="Login",
                        values={"username": username_raw, "password": password_raw},
                        error="Invalid username or password.",
                    )
                    continue
            except Exception as exc:
                event = yield LoginState(
                    screen_id="Login",
                    values={"username": username_raw, "password": password_raw},
                    error=str(exc),
                )
                continue

            user = User(user_id=record["id"], username=u, score=Score(record.get("score", 0)))
            characters = _char_repo.get_characters_for_user(user.user_id)
            event = yield CharacterSelectState(
                screen_id="CharacterSelect",
                user_id=user.user_id,
                username=u.value,
                characters=characters,
            )
            continue

        if event.name == "character_select.back":
            event = yield _TITLE_STATE
            continue

        if event.name == "character_select.new":
            user_id = event.payload.get("user_id", "")
            username = event.payload.get("username", "")
            event = yield CharacterCreateState(
                screen_id="CharacterCreate",
                user_id=user_id,
                username=username,
            )
            continue

        if event.name == "character_select.choose":
            user_id = event.payload.get("user_id", "")
            username = event.payload.get("username", "")
            characters = _char_repo.get_characters_for_user(user_id)
            event = yield CharacterSelectState(
                screen_id="CharacterSelect",
                user_id=user_id,
                username=username,
                characters=characters,
            )
            continue

        if event.name == "character_create.back":
            user_id = event.payload.get("user_id", "")
            username = event.payload.get("username", "")
            characters = _char_repo.get_characters_for_user(user_id)
            event = yield CharacterSelectState(
                screen_id="CharacterSelect",
                user_id=user_id,
                username=username,
                characters=characters,
            )
            continue

        if event.name == "character_create.submit":
            user_id = event.payload.get("user_id", "")
            username = event.payload.get("username", "")
            name = event.payload.get("name", "")
            class_value = event.payload.get("character_class", CharacterClass.WARRIOR.value)
            try:
                character_class = CharacterClass(class_value)
            except ValueError:
                character_class = CharacterClass.WARRIOR
            try:
                _char_repo.create_character(
                    user_id=user_id,
                    name=name,
                    character_class=character_class,
                )
            except CharacterAlreadyExists as exc:
                event = yield CharacterCreateState(
                    screen_id="CharacterCreate",
                    user_id=user_id,
                    username=username,
                    error=str(exc),
                )
                continue
            except Exception as exc:
                event = yield CharacterCreateState(
                    screen_id="CharacterCreate",
                    user_id=user_id,
                    username=username,
                    error=str(exc),
                )
                continue
            characters = _char_repo.get_characters_for_user(user_id)
            event = yield CharacterSelectState(
                screen_id="CharacterSelect",
                user_id=user_id,
                username=username,
                characters=characters,
            )
            continue

        if event.name == "register.back":
            event = yield (_logged_in_menu_state(current_user) if current_user else _TITLE_STATE)
            continue

        if event.name == "register.submit":
            username_raw = event.payload.get("username", "")
            password_raw = event.payload.get("password", "")

            try:
                u = Username(username_raw)
                u.value = username_raw
                p = Password(password_raw)
            except (TypeError, ValueError) as exc:
                event = yield RegistrationState(
                    screen_id="Register",
                    values={"username": username_raw, "password": password_raw, "confirm_password": ""},
                    error=str(exc),
                )
                continue

            try:
                _repo.save_user(u, p)
            except UserAlreadyExists:
                event = yield RegistrationState(
                    screen_id="Register",
                    values={"username": username_raw, "password": password_raw, "confirm_password": ""},
                    error=f"User '{u.value}' already exists.",
                )
                continue
            except Exception as exc:
                event = yield RegistrationState(
                    screen_id="Register",
                    values={"username": username_raw, "password": password_raw, "confirm_password": ""},
                    error=str(exc),
                )
                continue

            event = yield _TITLE_STATE
            continue

        if event.name in {"settings.back", "settings.save"}:
            event = yield (_logged_in_menu_state(current_user) if current_user else _TITLE_STATE)
            continue

        event = yield (_logged_in_menu_state(current_user) if current_user else _TITLE_STATE)


def main() -> None:
    ScreenManager().run(state_stream=app_flow())


if __name__ == "__main__":
    main()
