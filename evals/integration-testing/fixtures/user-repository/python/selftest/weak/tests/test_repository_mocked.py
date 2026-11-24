from unittest.mock import MagicMock

from accounts.repository import UserRepository


def test_save_runs_an_insert():
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (1,)
    UserRepository(conn).save("a@example.com", "A")
    sql = conn.cursor.return_value.__enter__.return_value.execute.call_args[0][0]
    assert sql.startswith("INSERT INTO users")
