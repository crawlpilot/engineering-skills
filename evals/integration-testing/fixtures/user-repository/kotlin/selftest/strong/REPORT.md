Seam: `UserRepository` against the database. Tests run against PostgreSQL 17 in a container (Testcontainers), with the schema built by the project's own `Migrations.apply`. Each test uses unique emails, so tests don't share data. Cases: save and find, the right user among several, case-insensitive lookup, not found, and a duplicate email rejected by the unique constraint. Named `UserRepositoryIT`, so failsafe runs it in `mvn verify`.

Ran the suite 3 consecutive times: 5 passed each time, about 4 s per run including container start.
