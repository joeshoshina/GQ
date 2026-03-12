from __future__ import annotations
from enum import Enum


class ScoreDisplay(Enum):
    NUMERIC = 0   # e.g. "1500"
    RANKED  = 1   # e.g. "Silver - 1500"

    def format(self, score: int) -> str:
        if self == ScoreDisplay.NUMERIC:
            return str(score)
        if score < 500:
            rank = "Bronze"
        elif score < 1500:
            rank = "Silver"
        elif score < 3000:
            rank = "Gold"
        else:
            rank = "Platinum"
        return f"{rank} · {score}"


class Settings:
    _instance: Settings | None = None
    _initialized: bool = False

    def __init__(self) -> None:
        if Settings._initialized:
            return
        self.score_display: ScoreDisplay = ScoreDisplay.NUMERIC
        Settings._initialized = True

    @classmethod
    def get_instance(cls) -> Settings:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def cycle_score_display(self) -> None:
        members = list(ScoreDisplay)
        next_idx = (self.score_display.value + 1) % len(members)
        self.score_display = members[next_idx]

    def format_score(self, score: int) -> str:
        return self.score_display.format(score)

    def to_dict(self) -> dict:
        return {"score_display": self.score_display.name}

    def apply_dict(self, data: dict) -> None:
        if "score_display" in data:
            try:
                self.score_display = ScoreDisplay[data["score_display"]]
            except KeyError:
                pass

    def __repr__(self) -> str:
        return f"Settings(score_display={self.score_display.name!r})"
