from ui import ScreenManager


def main() -> None:
    """Create and run the ScreenManager (blocks until the UI loop exits)."""
    manager = ScreenManager()
    manager.run()


if __name__ == "__main__":
    main()
