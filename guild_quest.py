from typing import Generator
import os

from ui import (
    ScreenManager,
    ScreenEvent,
    ScreenState,
    MenuState,
    MenuOption,
    RegistrationState,
)

from persistence import get_default_repository, UserAlreadyExists
from guild_quest_subsystem.user import Username, Password

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
            if option_id in ("Login", "Settings"):
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
                event = yield MenuState(
                    screen_id="Register",
                    title="Registration Error",
                    subtitle=str(exc),
                    options=[MenuOption(id="Back", label="Back")],
                )
                continue

            try:
                _repo.save_user(u, p)
            except UserAlreadyExists:
                event = yield MenuState(
                    screen_id="Register",
                    title="Registration Failed",
                    subtitle=f"User '{u.value}' already exists.",
                    options=[MenuOption(id="Back", label="Back")],
                )
                continue
            except Exception as exc:
                event = yield MenuState(
                    screen_id="Register",
                    title="Registration Failed",
                    subtitle=str(exc),
                    options=[MenuOption(id="Back", label="Back")],
                )
                continue

            event = yield _TITLE_STATE
            continue

        event = yield _TITLE_STATE


def main() -> None:
    ScreenManager().run(state_stream=app_flow())


if __name__ == "__main__":
    main()
