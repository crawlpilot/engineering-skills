"""UserRepository against real PostgreSQL, schema built by the project's migrations."""

import uuid

import psycopg
import pytest
from testcontainers.community.postgres import PostgresContainer

from accounts.migrate import apply_migrations
from accounts.repository import DuplicateEmailError, UserRepository

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def database_url():
    with PostgresContainer("postgres:17-alpine", driver=None) as pg:
        url = pg.get_connection_url()
        with psycopg.connect(url) as conn:
            apply_migrations(conn)
        yield url


@pytest.fixture
def repo(database_url):
    with psycopg.connect(database_url) as conn:
        yield UserRepository(conn)


def unique_email(prefix: str = "user") -> str:
    # Unique per test, so tests never see each other's rows.
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def test_saves_and_finds_a_user(repo):
    email = unique_email()
    saved = repo.save(email, "Ada")
    assert repo.find_by_email(email) == saved


def test_finds_the_right_user_among_several(repo):
    first, second = unique_email("first"), unique_email("second")
    repo.save(first, "First")
    saved = repo.save(second, "Second")
    assert repo.find_by_email(second) == saved


def test_lookup_ignores_case(repo):
    email = unique_email()
    saved = repo.save(email, "Ada")
    assert repo.find_by_email(email.upper()) == saved


def test_returns_none_when_not_found(repo):
    assert repo.find_by_email(unique_email("missing")) is None


def test_rejects_a_duplicate_email_in_any_case(repo):
    email = unique_email()
    repo.save(email, "Ada")
    with pytest.raises(DuplicateEmailError):
        repo.save(email.upper(), "Imposter")
