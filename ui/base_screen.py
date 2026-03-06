import abc
from typing import Any, Optional


class BaseScreen(abc.ABC):
    def __init__(self, stdscr: "Any") -> None:
        self.stdscr = stdscr
        self._running = True
        self._state: Optional[Any] = None

    def run(self) -> Optional[object]:
        try:
            self.on_enter()
            while self._running:
                try:
                    self.render()
                except Exception:
                    try:
                        self.stdscr.refresh()
                    except Exception:
                        pass

                try:
                    key = self.stdscr.getch()
                except Exception:
                    break

                try:
                    result = self.handle_key(key)
                except Exception:
                    result = None

                if result is not None:
                    return result
        finally:
            try:
                self.on_exit()
            except Exception:
                pass

        return None

    def on_enter(self) -> None:
        return None

    def on_exit(self) -> None:
        return None

    def set_state(self, state: Any) -> None:
        self._state = state

    def get_state(self) -> Optional[Any]:
        return self._state

    def stop(self) -> None:
        self._running = False

    @abc.abstractmethod
    def render(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def handle_key(self, key: int) -> Optional[object]:
        raise NotImplementedError
