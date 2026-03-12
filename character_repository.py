from __future__ import annotations

import json
import os
import tempfile
import threading
import uuid
from typing import Dict, List, Optional

from guild_quest_subsystem.enums import CharacterClass


class CharacterPersistenceError(Exception):
    pass


class CharacterNotFound(CharacterPersistenceError):
    pass


class CharacterAlreadyExists(CharacterPersistenceError):
    pass


class CharacterRecord:
    def __init__(
        self,
        character_id: str,
        user_id: str,
        name: str,
        character_class: CharacterClass,
        level: int,
        inventory: Optional[List[Dict]] = None,
    ) -> None:
        self.character_id: str = character_id
        self.user_id: str = user_id
        self.name: str = name
        self.character_class: CharacterClass = character_class
        self.level: int = level
        self.inventory: List[Dict] = inventory if inventory is not None else []

    def to_dict(self) -> Dict:
        return {
            "character_id": self.character_id,
            "user_id": self.user_id,
            "name": self.name,
            "character_class": self.character_class.value,
            "level": self.level,
            "inventory": list(self.inventory),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CharacterRecord":
        raw_class = data.get("character_class", CharacterClass.WARRIOR.value)
        try:
            character_class = CharacterClass(raw_class)
        except ValueError:
            character_class = CharacterClass.WARRIOR
        return cls(
            character_id=data["character_id"],
            user_id=data["user_id"],
            name=str(data.get("name", "")),
            character_class=character_class,
            level=int(data.get("level", 1)),
            inventory=list(data.get("inventory", [])),
        )

    def __repr__(self) -> str:
        return (
            f"CharacterRecord(name={self.name!r}, class={self.character_class.value!r}, "
            f"level={self.level}, user_id={self.user_id!r})"
        )


class CharacterRepository:
    def __init__(self, path: str = "characters.json") -> None:
        if not isinstance(path, str):
            raise TypeError("path must be a string")
        self._path = path
        dirpath = os.path.dirname(self._path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        self._lock = threading.RLock()
        with self._lock:
            if not os.path.exists(self._path):
                self._atomic_write([])

    def _read_all(self) -> List[Dict]:
        with self._lock:
            try:
                with open(self._path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if not isinstance(data, list):
                    raise CharacterPersistenceError(
                        "characters file corrupted: expected a list"
                    )
                return [entry for entry in data if isinstance(entry, dict)]
            except FileNotFoundError:
                return []
            except json.JSONDecodeError as exc:
                raise CharacterPersistenceError(
                    f"invalid JSON in characters file: {exc}"
                ) from exc

    def _atomic_write(self, data: List[Dict]) -> None:
        serialized = json.dumps(data, indent=2, ensure_ascii=False)
        dirpath = os.path.dirname(self._path) or "."
        fd, tmp_path = tempfile.mkstemp(prefix=".tmp_chars_", dir=dirpath)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(serialized)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_path, self._path)
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    def get_characters_for_user(self, user_id: str) -> List[CharacterRecord]:
        return [
            CharacterRecord.from_dict(entry)
            for entry in self._read_all()
            if entry.get("user_id") == user_id
        ]

    def get_character(self, character_id: str) -> Optional[CharacterRecord]:
        for entry in self._read_all():
            if entry.get("character_id") == character_id:
                return CharacterRecord.from_dict(entry)
        return None

    def create_character(
        self,
        user_id: str,
        name: str,
        character_class: CharacterClass = CharacterClass.WARRIOR,
        level: int = 1,
    ) -> CharacterRecord:
        if not user_id:
            raise ValueError("user_id must not be empty")
        name = name.strip()
        if not name:
            raise ValueError("Character name must not be empty")
        if len(name) > 24:
            raise ValueError("Character name must be 24 characters or fewer")
        if not isinstance(character_class, CharacterClass):
            raise TypeError("character_class must be a CharacterClass instance")
        if level < 1:
            raise ValueError("level must be at least 1")

        with self._lock:
            records = self._read_all()

            # Duplicate-name guard (per user)
            for entry in records:
                if (
                    entry.get("user_id") == user_id
                    and entry.get("name", "").lower() == name.lower()
                ):
                    raise CharacterAlreadyExists(
                        f"A character named '{name}' already exists for this account."
                    )

            character_id = str(uuid.uuid4())
            new_entry: Dict = {
                "character_id": character_id,
                "user_id": user_id,
                "name": name,
                "character_class": character_class.value,
                "level": level,
                "inventory": [],
            }
            records.append(new_entry)
            self._atomic_write(records)
            return CharacterRecord.from_dict(new_entry)

    def update_character(self, record: CharacterRecord) -> None:
        with self._lock:
            records = self._read_all()
            for i, entry in enumerate(records):
                if entry.get("character_id") == record.character_id:
                    records[i] = record.to_dict()
                    self._atomic_write(records)
                    return
            raise CharacterNotFound(record.character_id)

    def delete_character(self, character_id: str) -> None:
        with self._lock:
            records = self._read_all()
            filtered = [e for e in records if e.get("character_id") != character_id]
            if len(filtered) == len(records):
                raise CharacterNotFound(character_id)
            self._atomic_write(filtered)

    def delete_all_for_user(self, user_id: str) -> int:
        with self._lock:
            records = self._read_all()
            filtered = [e for e in records if e.get("user_id") != user_id]
            deleted = len(records) - len(filtered)
            if deleted:
                self._atomic_write(filtered)
            return deleted

    def clear_all(self) -> None:
        with self._lock:
            self._atomic_write([])


_default_char_repo: Optional[CharacterRepository] = None


def get_default_character_repository(path: Optional[str] = None) -> CharacterRepository:
    global _default_char_repo
    if _default_char_repo is None:
        _default_char_repo = CharacterRepository(path=path or "characters.json")
    return _default_char_repo
