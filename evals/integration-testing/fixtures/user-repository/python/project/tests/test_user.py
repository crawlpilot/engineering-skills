from accounts.repository import User


def test_users_compare_by_value():
    assert User(1, "a@example.com", "A") == User(1, "a@example.com", "A")
