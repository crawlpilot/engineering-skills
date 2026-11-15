# Unit testing: Python

Use what the project already has. These are the defaults for pytest; if the project uses `unittest`, follow its style instead.

## Find and run

Look in `pyproject.toml`, `pytest.ini`, `tox.ini`, `noxfile.py` and the CI config for the command and options.

| Goal | Command |
| --- | --- |
| Everything | `pytest` (or `uv run pytest`, `poetry run pytest`, `tox`) |
| One file | `pytest tests/test_pricing.py` |
| One test | `pytest tests/test_pricing.py::test_rejects_negative_quantity` |
| By name | `pytest -k "negative and quantity"` |
| Stop at first failure, show locals | `pytest -x -l` |

Tests live where the project puts them, usually `tests/` mirroring the package. Files are `test_*.py`; functions are `test_*`.

## Shape of a test

```python
def test_applies_tax_to_net_price():
    calculator = PriceCalculator(tax_rates=FixedTaxRates(Decimal("0.20")))

    total = calculator.total_for(make_order(items=[make_item(price="10.00")]))

    assert total == Money("12.00")


def test_rejects_negative_quantity():
    calculator = PriceCalculator(tax_rates=FixedTaxRates(Decimal("0.20")))
    order = make_order(items=[make_item(quantity=-1)])

    with pytest.raises(ValueError, match="quantity"):
        calculator.total_for(order)
```

- Plain `assert` with literal expected values. pytest shows both sides on failure.
- Build inputs with small factory functions that take keyword overrides and supply sensible defaults.
- `pytest.raises` with `match=` checks the type and the message. Put only the call that should raise inside the block.
- Compare floats with `pytest.approx`. Use `Decimal` for money.

## Same shape, many inputs

```python
@pytest.mark.parametrize(
    ("quantity", "expected"),
    [
        (0, Tier.FREE),
        (1, Tier.STANDARD),
        (49, Tier.STANDARD),
        (50, Tier.BULK),
    ],
)
def test_picks_tier_by_quantity(quantity, expected):
    assert Tier.for_quantity(quantity) == expected
```

Add `ids=[...]` or `pytest.param(..., id="...")` when the values alone do not explain the case.

## Fixtures

- Use a fixture for the object under test and its collaborators. Keep values a test depends on in the test body, not hidden in a fixture.
- Default to function scope. A wider scope shares state between tests.
- Put shared fixtures in the nearest `conftest.py`, not a global one.
- `tmp_path` for files, `monkeypatch` for environment variables and attributes, `caplog` and `capsys` only when the log or output is the behaviour.

## Time and randomness

Pass them in:

```python
def is_expired(token: Token, now: datetime) -> bool:
    return token.expires_at <= now


def test_token_expires_at_the_boundary():
    token = make_token(expires_at=datetime(2026, 1, 15, 10, 0, tzinfo=UTC))

    assert is_expired(token, now=datetime(2026, 1, 15, 10, 0, tzinfo=UTC))
```

If the code reads the clock inline, the seam is a `now` parameter or an injected clock callable. Use a time-freezing library only if the project already depends on one. Always use timezone-aware datetimes.

## Doubles

Prefer a small fake:

```python
class InMemoryOrderRepository:
    def __init__(self):
        self._orders = {}

    def save(self, order):
        self._orders[order.id] = order

    def find(self, order_id):
        return self._orders.get(order_id)
```

With `unittest.mock`, when an interaction is the behaviour:

```python
def test_sends_welcome_email_on_signup():
    mailer = create_autospec(Mailer, instance=True)

    SignupService(InMemoryUserRepository(), mailer).sign_up("a@example.com")

    mailer.send.assert_called_once_with("a@example.com", subject="Welcome")
```

- Use `create_autospec` or `spec=`. A bare `Mock()` accepts any call, so a misspelled method passes silently.
- Patch where the name is looked up, not where it is defined: `monkeypatch.setattr("app.billing.requests", fake)`, not the `requests` module itself.
- Do not patch the unit under test or its private helpers.

## Proving a test can fail

```bash
# edit the production line the test targets, then:
pytest tests/test_pricing.py::test_applies_tax_to_net_price
git diff --stat   # must show no production change left behind
```

## Common mistakes

- A test with no assertion, or `assert mock.called_once()` (a truthy attribute, not a check). Use `assert_called_once()`.
- Mutable default arguments in test factories leaking state between tests.
- Module-level setup that runs at import.
- Asserting on the full text of an error message; match the stable part.
- `time.sleep` in a unit test.
