"""
Simulates a database for persistent user profile information. Uses atomic operations for read/write
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
import hashlib
from typing import Optional, List, Dict

from guild_quest_subsystem.user import Username, Password


class PersistenceError(Exception):
    pass

class UserAlreadyExists(PersistenceError):
    pass

class UserNotFound(PersistenceError):
    pass

class InsecureRecordError(PersistenceError):
    pass


class UserRepository:
    def __init__(self, path: str = "users.json") -> None:
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


    def _read_all(self) -> List[Dict[str, str]]:
        with self._lock:
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    raise PersistenceError("persistence file corrupted: expected a list")
                users = []
                for entry in data:
                    if isinstance(entry, dict):
                        users.append(entry)
                return users
            except FileNotFoundError:
                return []
            except json.JSONDecodeError as e:
                raise PersistenceError(f"invalid JSON in persistence file: {e}")

    def _atomic_write(self, data: List[Dict[str, str]]) -> None:
        serialized = json.dumps(data, indent=2, ensure_ascii=False)
        dirpath = os.path.dirname(self._path) or "."
        fd, tmp_path = tempfile.mkstemp(prefix=".tmp_users_", dir=dirpath)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(serialized)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self._path)
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    @staticmethod
    def _generate_salt(length: int = 16) -> bytes:
        return os.urandom(length)

    @staticmethod
    def _hash_password(password: Password, salt: bytes) -> str:
        raw = password.value.encode("utf-8")
        dk = hashlib.pbkdf2_hmac("sha256", raw, bytes(salt), 100_000)
        return dk.hex()

    def list_usernames(self) -> List[str]:
        users = self._read_all()
        return [u.get("username", "") for u in users]

    def get_user(self, username: Username | str) -> Optional[Dict[str, str]]:
        name = username.value if isinstance(username, Username) else username
        users = self._read_all()
        for u in users:
            if u.get("username") == name:
                return dict(u)
        return None

    def save_user(self, username: Username, password: Password) -> None:
        if not isinstance(username, Username):
            raise TypeError("username must be a Username instance")
        if not isinstance(password, Password):
            raise TypeError("password must be a Password instance")
        with self._lock:
            users = self._read_all()
            for u in users:
                if u.get("username") == username.value:
                    raise UserAlreadyExists(username.value)
            salt = self._generate_salt()
            password_hash = self._hash_password(password, salt)
            record = {
                "username": username.value,
                "password_hash": password_hash,
                "salt": salt.hex(),
                "score": 0,
            }
            users.append(record)
            self._atomic_write(users)

    def update_password(self, username: Username, new_password: Password) -> None:
        if not isinstance(username, Username):
            raise TypeError("username must be a Username instance")
        if not isinstance(new_password, Password):
            raise TypeError("new_password must be a Password instance")
        with self._lock:
            users = self._read_all()
            for u in users:
                if u.get("username") == username.value:
                    salt = self._generate_salt()
                    u["password_hash"] = self._hash_password(new_password, salt)
                    u["salt"] = salt.hex()
                    self._atomic_write(users)
                    return
            raise UserNotFound(username.value)

    def delete_user(self, username: Username | str) -> None:
        name = username.value if isinstance(username, Username) else username
        with self._lock:
            users = self._read_all()
            new_users = [u for u in users if u.get("username") != name]
            if len(new_users) == len(users):
                raise UserNotFound(name)
            self._atomic_write(new_users)

    def verify_password(self, username: Username | str, password: Password) -> bool:
        name = username.value if isinstance(username, Username) else username
        if not isinstance(password, Password):
            raise TypeError("password must be a Password instance")
        user = self.get_user(name)
        if not user:
            return False
        stored = user.get("password_hash", "")
        salt_hex = user.get("salt")
        if not salt_hex:
            raise InsecureRecordError(f"user '{name}' record missing required salt")
        try:
            salt = bytes.fromhex(salt_hex)
        except Exception:
            raise InsecureRecordError(f"user '{name}' record contains invalid salt")
        computed = self._hash_password(password, salt)
        return computed == stored

    def clear_all(self) -> None:
        with self._lock:
            self._atomic_write([])


_default_repo: Optional[UserRepository] = None


def get_default_repository(path: Optional[str] = None) -> UserRepository:
    global _default_repo
    if _default_repo is None:
        _default_repo = UserRepository(path=path or "users.json")
    return _default_repo

default_repository: UserRepository = get_default_repository()
