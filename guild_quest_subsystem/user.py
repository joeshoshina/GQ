# GQ/guild_quest_subsystem/user.py
import re
from typing import Any, Dict, List, Optional


class Username:
    def __init__(self, value: str):
        self.value = value  # use setter validation

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, v: str) -> None:
        if not isinstance(v, str):
            raise TypeError("username must be a string")
        v = v.strip()
        if not v:
            raise ValueError("username cannot be empty or only whitespace")
        if not (3 <= len(v) <= 30):
            raise ValueError("username must be between 3 and 30 characters")
        if not re.fullmatch(r"[A-Za-z0-9_]+", v):
            raise ValueError("username may contain only letters, digits, and underscores")
        self._value = v

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Username({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Username):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


class Password:
    def __init__(self, value: str):
        self.value = value  # use setter validation

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, v: str) -> None:
        if not isinstance(v, str):
            raise TypeError("password must be a string")
        if not (6 <= len(v) <= 30):
            raise ValueError("password must be between 6 and 30 characters long")
        self._value = v

    def __str__(self) -> str:
        return "Password{**SENSITIVE VALUE HIDDEN**}"

    def __repr__(self) -> str:
        return "Password(<hidden>)"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Password):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


class Score:
    def __init__(self, value: int):
        self.value = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v: int) -> None:
        if not isinstance(v, int) or isinstance(v, bool):
            raise TypeError("score must be an int")
        if v < 0:
            raise ValueError("score must be non-negative")
        self._value = v

    def __int__(self) -> int:
        return self._value

    def __index__(self) -> int:
        return self._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"Score({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Score):
            return self._value == other._value
        if isinstance(other, int) and not isinstance(other, bool):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


class User:
    def __init__(
        self,
        user_id: int,
        username: Optional[Username] = None,
    ) -> None:
        if not isinstance(user_id, int) or isinstance(user_id, bool):
            raise TypeError("user_id must be an int")
        self.id: int = user_id
        self.username: Optional[Username] = username
        self.characters: List[Any] = []

    def add_character(self, char: Any) -> None:
        self.characters.append(char)

    def remove_character(self, index: int) -> Any:
        return self.characters.pop(index)

    def list_characters(self) -> List[Any]:
        return list(self.characters)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": str(self.username) if self.username else None,
            "characters": list(self.characters),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        uid = data.get("id")
        username_val = data.get("username")
        username = Username(username_val) if username_val is not None else None
        u = cls(user_id=uid, username=username)
        u.characters = list(data.get("characters", []))
        return u

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, characters={len(self.characters)})"
