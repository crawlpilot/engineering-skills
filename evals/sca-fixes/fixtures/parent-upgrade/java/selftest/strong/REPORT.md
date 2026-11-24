GHSA-w33c-445m-f8w7 (CVE-2023-3635, GzipSource denial of service) is in okio 2.8.0, fixed in 3.4.0. Path: weather -> okhttp 4.9.0 -> okio 2.8.0.

Parent upgrade first: okhttp 4.12.0, the latest 4.x, depends on okio 3.6.0, so bumping okhttp 4.9.0 -> 4.12.0 clears it without an override or a major version. No API this project uses changed.

Verified: `mvn dependency:tree -Dincludes=com.squareup.okio` now shows okio 3.6.0, and `mvn test` passes.
