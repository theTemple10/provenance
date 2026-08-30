"""User models and in-memory user store."""

import uuid
import hashlib
import secrets
from datetime import datetime, timezone


class User:
    def __init__(self, username: str, email: str, password_hash: str, salt: str):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.salt = salt
        self.role = "user"
        self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
        }


class UserStore:
    """In-memory store for users."""

    def __init__(self):
        self._users: dict[str, User] = {}
        self._by_username: dict[str, User] = {}

    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple[str, str]:
        if salt is None:
            salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100000
        )
        return password_hash.hex(), salt

    def create_user(self, username: str, email: str, password: str) -> User:
        password_hash, salt = self.hash_password(password)
        user = User(username=username, email=email, password_hash=password_hash, salt=salt)
        self._users[user.id] = user
        self._by_username[username] = user
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        return self._by_username.get(username)

    def verify_password(self, username: str, password: str) -> User | None:
        user = self.get_by_username(username)
        if user is None:
            return None
        password_hash, _ = self.hash_password(password, user.salt)
        if password_hash == user.password_hash:
            return user
        return None

    def list_all(self) -> list[dict]:
        return [user.to_dict() for user in self._users.values()]

    def count(self) -> int:
        return len(self._users)
