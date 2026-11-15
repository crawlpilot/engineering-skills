# Integration testing: Python

Use what the project already has. These are common defaults for pytest; check library APIs against the versions installed.

## Separate them from unit tests

Use a marker or a directory, whichever the project already does:

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = ["integration: needs real services (containers)"]
```

```bash
pytest -m "not integration"     # fast suite
pytest -m integration           # integration stage
```

Register the marker; with `--strict-markers` an unregistered one is an error.

## Real database with testcontainers

```python
# tests/integration/conftest.py
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url()


@pytest.fixture
def db(postgres_url):
    engine = create_engine(postgres_url)
    run_migrations(engine)          # the project's real migrations
    with engine.begin() as conn:
        truncate_all(conn)          # each test starts from empty tables
    yield engine
    engine.dispose()
```

```python
# tests/integration/test_order_repository.py
pytestmark = pytest.mark.integration


def test_finds_saved_order_by_id(db):
    repo = OrderRepository(db)
    order = make_order(order_id=uuid4())

    repo.save(order)

    assert repo.find(order.id) == order


def test_rejects_duplicate_order_id(db):
    repo = OrderRepository(db)
    order = make_order(order_id=uuid4())
    repo.save(order)

    with pytest.raises(DuplicateOrderError):
        repo.save(order)
```

- Start the container once per session; isolate data per test by truncating, by rolling back a wrapping transaction, or by unique keys.
- Pin the image to the major version production runs.
- Run the real migrations (Alembic, Django migrations) so the schema under test is the one that ships.
- Use the production database engine. SQLite in place of PostgreSQL hides type, constraint and locking differences.
- With Django, use `pytest-django`'s `db` or `transactional_db` fixtures and the project's test settings.

## HTTP dependencies

Stub at the transport level so the real client code, serialisation and error handling run. Use the library that matches the HTTP client the project uses: `responses` for `requests`, `respx` for `httpx`.

```python
@respx.mock
def test_surfaces_declined_payment():
    respx.post("https://pay.example.test/v1/charges").mock(
        return_value=httpx.Response(402, json={"code": "card_declined"})
    )
    client = PaymentClient(base_url="https://pay.example.test", timeout=2.0)

    with pytest.raises(PaymentDeclined):
        client.charge(make_charge())
```

Cover the failure modes explicitly: a 5xx, a timeout (`side_effect=httpx.TimeoutException("slow")`), a connection error, and a malformed body. Keep stubs honest with a contract test against the provider's published schema.

To test your own HTTP API, drive it through the framework's test client (`TestClient` for FastAPI and Starlette, Django's `Client`, Flask's `test_client`) with real routing, validation and serialisation, and the real database fixture above.

## Asynchronous behaviour

Wait on a condition with a deadline, never a fixed sleep:

```python
def wait_until(predicate, timeout=10.0, interval=0.1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(interval)
    raise AssertionError(f"condition not met within {timeout}s")


def test_publishes_order_placed(db, broker):
    place_order(db, broker, order_id := uuid4())

    wait_until(lambda: order_placed(order_id) in broker.received())
```

For `asyncio` code, use the project's async test plugin and `asyncio.wait_for` with a timeout.

## Stability checks

```bash
pytest -m integration tests/integration/test_order_repository.py
for i in 1 2 3; do pytest -q -m integration tests/integration/test_order_repository.py || break; done
```

If the project has `pytest-randomly` or `pytest-xdist`, also run with random order and in parallel. Typical causes of flakiness: fixed sleeps, shared rows without cleanup, fixed ports, naive datetimes, and test order.
