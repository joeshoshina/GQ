# GQ/guild_quest_subsystem/user.py
import re
import uuid
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




class User:
    def __init__(
        self,
        user_id: str,
        username: Optional[Username] = None,
    ) -> None:
        if not isinstance(user_id, str) or isinstance(user_id, bool):
            raise TypeError("user_id must be a UUID string")
        user_id = user_id.strip()
        if not user_id:
            raise ValueError("user_id cannot be empty")
        try:
            uuid.UUID(user_id)
        except (ValueError, AttributeError, TypeError):
            raise ValueError("user_id must be a valid UUID string")
        self.user_id: str = user_id
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
            "user_id": self.user_id,
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
        return f"User(user_id={self.user_id!r}, username={self.username!r}, characters={len(self.characters)})"
