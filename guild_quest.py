from typing import Generator
import os

from ui import (
    ScreenManager,
    ScreenEvent,
    ScreenState,
    MenuState,
    MenuOption,
    RegistrationState,
    LoginState,
)

from persistence import get_default_repository, UserAlreadyExists
from guild_quest_subsystem.user import Username, Password, User

_BASE_DIR = os.path.dirname(__file__)
_DATA_FILE = os.path.join(_BASE_DIR, "data", "users.json")
_repo = get_default_repository(path=_DATA_FILE)


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


def app_flow() -> Generator[ScreenState, ScreenEvent, None]:
    event = yield _TITLE_STATE
    while True:
        if event is None:
            event = yield _TITLE_STATE
            continue

        # Menu navigation events
        if event.name == "menu.select":
            option_id = event.payload.get("option_id", "")
            if option_id == "Exit":
                return
            if option_id == "Register":
                event = yield RegistrationState(screen_id="Register")
                continue
            if option_id == "Login":
                event = yield LoginState(screen_id="Login")
                continue
            if option_id == "Settings":
                event = yield MenuState(
                    screen_id=option_id,
                    title=option_id,
                    subtitle="Not implemented",
                    options=[MenuOption(id="Back", label="Back")],
                )
                continue
            if option_id == "Back":
                event = yield _TITLE_STATE
                continue

        if event.name == "login.back":
            event = yield _TITLE_STATE
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

            user = User(user_id=record["id"], username=u)
            event = yield _TITLE_STATE
            continue

        if event.name == "register.back":
            event = yield _TITLE_STATE
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

        event = yield _TITLE_STATE


def main() -> None:
    ScreenManager().run(state_stream=app_flow())


if __name__ == "__main__":
    main()
