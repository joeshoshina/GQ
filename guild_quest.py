from typing import Generator

from ui import (
    ScreenManager,
    ScreenEvent,
    ScreenState,
    MenuState,
    MenuOption,
    RegistrationState,
)

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
            username = event.payload.get("username", "")
            password = event.payload.get("password", "")
            _ = (username, password)
            event = yield _TITLE_STATE
            continue
        event = yield _TITLE_STATE

def main() -> None:
    ScreenManager().run(state_stream=app_flow())

if __name__ == "__main__":
    main()