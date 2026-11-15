# Code review: Python

Language-specific things to look for, after the general checklist. Each is a prompt to check, not an automatic finding: confirm it applies before reporting it.

## Verify, if the tools are present

Use the project's own commands from `pyproject.toml`, `tox.ini`, `noxfile.py`, the Makefile or CI config. Typical ones:

```bash
ruff check .          # or flake8 / pylint, whichever the project uses
ruff format --check . # or black --check .
mypy .                # or pyright
pytest -q
```

Do not report as findings things the configured linter or formatter already enforces.

## Correctness

- **Mutable defaults.** `def f(items=[])` or `={}`; the object is shared across calls. Expect `None` and creation inside the function.
- **Truthiness.** `if x:` where `0`, `""` or an empty collection is a valid value and `is None` was meant. `== None` instead of `is None`.
- **Identity.** `is` used to compare values such as strings or numbers.
- **Closures.** A lambda or inner function defined in a loop that captures the loop variable by reference.
- **Numbers.** `float` for money (expect `Decimal` or integer minor units); floats compared with `==`.
- **Time.** Naive `datetime` values; `datetime.now()` or `utcnow()` without a timezone; the clock read inline in logic that should take `now` as a parameter.
- **Iteration.** Mutating a list or dict while iterating it; a generator consumed twice; relying on set ordering.
- **Class attributes.** A mutable class-level attribute used as if it were per-instance.
- **Shadowing.** A local or module named after a builtin or standard-library module (`list`, `id`, `json.py`).

## Errors and resources

- Bare `except:` or `except Exception:` that does not re-raise or sit at a deliberate isolation boundary.
- An exception swallowed with `pass`, or logged and then ignored.
- `raise NewError(...)` inside an `except` without `from err`, losing the cause.
- `assert` used for input validation or control flow in production code; it is removed under `-O`.
- Files, sockets, locks or sessions opened without `with`.
- A `try` block that wraps far more than the line that can fail.

## Concurrency and async

- A blocking call (`requests`, `time.sleep`, file or database I/O) inside an `async def`.
- A coroutine called without `await`, or a task created and never awaited or stored.
- Shared mutable state across threads without a lock; assumptions that the interpreter lock makes compound operations atomic.
- Missing timeouts on network calls. `requests` has no default timeout.

## Types and API

- Public functions without annotations where the project annotates; `Any` or `# type: ignore` added without a reason.
- Implicit optional (`x: str = None`) instead of `str | None`.
- A function returning different types on different paths.
- Concrete container types in signatures where an abstract one (`Sequence`, `Mapping`) would do.
- New module-level side effects at import time.
- A `@property` doing expensive or failing work.

## Security prompts

Flag and recommend specialist review; do not treat this list as an audit.

- SQL built with f-strings or `%` formatting instead of bound parameters.
- `subprocess` with `shell=True` and any non-constant input; `os.system`.
- `eval`, `exec`, `pickle.loads`, or `yaml.load` without a safe loader, on untrusted data.
- Secrets, tokens or personal data in logs or exception messages.
- File paths built from user input without resolving and checking against a base directory.
- `random` used for tokens or keys where `secrets` is required.
- `verify=False` on HTTP calls.
- Template rendering with autoescape disabled.

## Framework prompts (when present)

- Django: a query inside a loop (missing `select_related` or `prefetch_related`); a migration that locks a large table or is not reversible; raw SQL with interpolation.
- FastAPI and Pydantic: validation bypassed by using raw dicts; blocking work inside async endpoints.
- SQLAlchemy: a session shared across requests or threads; missing commit or rollback on error paths.

## Tests in the change

- A test with no assertion, or `mock.called_once()` used as if it asserted.
- `Mock()` without a spec; patching at the definition site instead of where the name is used.
- Fixtures with a wider scope than needed, carrying state between tests.
- `time.sleep` in tests.
