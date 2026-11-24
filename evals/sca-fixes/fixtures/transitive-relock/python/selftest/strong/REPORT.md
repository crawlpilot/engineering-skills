GHSA-pq67-6m6q-mj2v (CVE-2025-50181) is in urllib3 2.2.1, fixed in 2.5.0. Path: weather -> requests 2.32.3 -> urllib3 2.2.1. requests allows `urllib3>=1.21.1,<3`, so no manifest change is needed.

Fix: `uv lock --upgrade-package urllib3`, which moved only urllib3 (2.2.1 -> 2.8.0). requests and everything else stay where they were.

Verified: `uv lock --check` passes, tests pass (1 passed), and uv.lock now resolves urllib3 2.8.0.
