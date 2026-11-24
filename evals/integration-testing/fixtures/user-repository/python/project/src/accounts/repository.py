"""User storage in PostgreSQL.

Emails are stored lower-cased and are unique, so lookups ignore case.
"""

from dataclasses import dataclass

import psycopg
from psycopg import errors


class DuplicateEmailError(Exception):
    """A user with this email already exists."""


@dataclass(frozen=True)
class User:
    id: int
    email: str
    name: str


class UserRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def save(self, email: str, name: str) -> User:
        """Inserts a user. Raises DuplicateEmailError if the email is taken, in any case."""
        email = email.lower()
        try:
            with self._conn.cursor() as cur:
                cur.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", (email, name))
                (user_id,) = cur.fetchone()
            self._conn.commit()
        except errors.UniqueViolation as exc:
            self._conn.rollback()
            raise DuplicateEmailError(email) from exc
        return User(user_id, email, name)

    def find_by_email(self, email: str) -> User | None:
        """Returns the user with this email, ignoring case, or None."""
        with self._conn.cursor() as cur:
            cur.execute("SELECT id, email, name FROM users WHERE email = %s", (email.lower(),))
            row = cur.fetchone()
        return User(*row) if row else None
