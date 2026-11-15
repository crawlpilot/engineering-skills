# Coding standards: Python

The project's own formatter, linter and type-checker configuration comes first. Where the project has none, these defaults follow PEP 8 and the Google Python Style Guide.

## Find and run

Look in `pyproject.toml`, `setup.cfg`, `tox.ini`, `noxfile.py`, `.pre-commit-config.yaml`, the Makefile and CI config. Use the tools the project declares, through its runner (`uv run`, `poetry run`, `tox`, `nox`, `make`).

| Job | Typical command |
| --- | --- |
| Format | `ruff format .` or `black .` |
| Lint | `ruff check .`, `flake8` or `pylint <package>` |
| Type check | `mypy .` or `pyright` |
| Tests | `pytest` |
| Everything the project wires up | `pre-commit run --all-files` |

Do not introduce a formatter or linter the project does not already use.

## Layout

- Four spaces per level, no tabs.
- Line length is whatever the project configures. The style guides differ (PEP 8 says 79, Google says 80, Black defaults to 88), so read the config rather than assuming.
- No backslash continuations; wrap inside parentheses, brackets or braces.
- Imports at the top, one module per line, grouped: standard library, third party, local. Absolute imports.
- Two blank lines around top-level definitions, one between methods.
- Executable logic in `main()` behind `if __name__ == "__main__":`. No side effects at import time.

## Naming

| Thing | Convention | Example |
| --- | --- | --- |
| Package, module | `lower_with_under` | `billing/invoice_store.py` |
| Class, exception | `CapWords`; exceptions end in `Error` | `InvoiceStore`, `InvoiceNotFoundError` |
| Function, method, variable, parameter | `lower_with_under` | `find_overdue_invoices` |
| Constant | `CAPS_WITH_UNDER` | `MAX_RETRIES` |
| Internal | leading underscore | `_parse_row` |
| Type variable | short CapWords | `T`, `RequestT` |

Avoid single-character names except counters and established notation. Do not put type information in names. Do not shadow builtins.

## Language rules

- No mutable default arguments. Use `None` and create the object inside the function.
- `is None` and `is not None` for None checks. Implicit falsiness for empty sequences (`if not users:`), unless zero or empty is a valid value distinct from None.
- Comprehensions for simple cases only: one `for` clause, at most one condition. Otherwise write the loop.
- f-strings for formatting. In logging calls, pass arguments to a literal pattern instead: `log.info("Invoice %s sent", invoice_id)`.
- `with` for files, locks, sessions and anything else that must be released.
- Avoid mutable global state. Module-level constants are fine.
- Properties only for cheap, attribute-like access.
- `pathlib.Path` over string path manipulation; timezone-aware datetimes; `Decimal` for money.

## Types

Annotate when the project does, and always for new public functions in a typed codebase.

- `X | None` written explicitly; never `x: str = None`.
- Built-in generics (`list[str]`, `dict[str, int]`); abstract types in parameters (`Sequence`, `Mapping`, `Iterable`).
- `dataclass` (often `frozen=True`) or the project's model library for structured data instead of loose dicts and tuples.
- `Protocol` for a structural interface; `Enum` for a closed set of values.
- A suppression is scoped to the line and carries a reason: `# type: ignore[arg-type]  # third-party stub is wrong`.

## Docstrings

Follow the style the project already uses (Google, NumPy or reStructuredText). In Google style:

```python
def find_overdue_invoices(customer_id: str, as_of: date) -> list[Invoice]:
    """Returns invoices for a customer that are unpaid past their due date.

    Args:
        customer_id: Identifier of the customer.
        as_of: Date to compare due dates against.

    Returns:
        Overdue invoices, oldest first. Empty if there are none.

    Raises:
        CustomerNotFoundError: If no customer has this identifier.
    """
```

Document public modules, classes and functions. Skip docstrings that only restate the name.

## Errors

- Raise the most specific built-in that fits (`ValueError`, `TypeError`, `KeyError`) or a project exception ending in `Error`.
- Never bare `except:`. Catch `Exception` only to re-raise or at a deliberate isolation boundary that records the error.
- Keep the cause: `raise InvoiceLoadError(f"invoice {invoice_id}") from err`.
- Keep `try` blocks small, around the line that can fail.
- No `assert` for validating input or state in production code.
- Error messages name what was expected and what was received, with interpolated values clearly marked.

## Suppressions

Scope to the line, name the rule, and give the reason:

```python
value = legacy_call()  # noqa: S301  # input is produced by our own exporter, never user-supplied
```
