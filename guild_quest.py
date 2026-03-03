"""Guild Quest entrypoint.

This module provides the application's main entrypoint and delegates UI control
to the `ScreenManager` implemented in the `ui` package.

It intentionally contains no game logic; it only wires up and runs the UI.
"""

from ui import ScreenManager


def main() -> None:
    """Create and run the ScreenManager (blocks until the UI loop exits)."""
    manager = ScreenManager()
    manager.run()


if __name__ == "__main__":
    main()
