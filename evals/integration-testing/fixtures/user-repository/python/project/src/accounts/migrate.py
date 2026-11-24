"""Applies the SQL files in migrations/, in name order. Production runs this on deploy."""

from pathlib import Path

import psycopg

MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"


def apply_migrations(conn: psycopg.Connection, directory: Path = MIGRATIONS) -> None:
    for path in sorted(directory.glob("*.sql")):
        conn.execute(path.read_text(encoding="utf-8"))
    conn.commit()
