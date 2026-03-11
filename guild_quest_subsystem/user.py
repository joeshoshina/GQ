import re

class Username:
    def __init__(self, value: str):
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, v: str):
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

    def __eq__(self, other) -> bool:
        if isinstance(other, Username):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


class Password:
    def __init__(self, value: str):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v: str):
        if not isinstance(v, str):
            raise TypeError("The password must be type string")
        if not (6 <= len(v) <= 30):
            raise ValueError("Password must be between 6 and 30 characters long")
        self._value = v

    def __str__(self):
        return "Password{**SENSITIVE VALUE HIDDEN**}"

    def __repr__(self) -> str:
        return f"Username({self._value!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Username):
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
    def value(self, v: int):
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

    def __eq__(self, other) -> bool:
        if isinstance(other, Score):
            return self._value == other._value
        if isinstance(other, int) and not isinstance(other, bool):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)
