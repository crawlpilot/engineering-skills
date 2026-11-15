---
name: sca-fixes
description: Fix known vulnerabilities in third-party dependencies reported by a scanner such as Snyk, Wiz, Trivy, Dependabot, OSV-Scanner, npm audit or pip-audit. Use when given a CVE or GHSA identifier, a scanner report, a failing security gate, or a request to upgrade a vulnerable package. Covers tracing transitive dependencies, choosing the smallest safe fix, applying it, and verifying by rebuild, test and rescan. Not for vulnerabilities in first-party code or in operating-system packages on hosts and images.
---

# SCA fixes

The vulnerable code lives in someone else's package, so the only fixes are: move to a version where it is fixed, remove the package, or record why it does not apply. Most findings are in transitive dependencies, which means the work is tracing the path back to something the project controls. A fix is not done until the project rebuilds, its tests pass, and the scanner no longer reports the finding.

## Read first

1. Identify the ecosystem and package manager, the manifest and the lockfile. A repo may have several.
2. Get the findings in the most precise form available: advisory identifier, package, installed version, fixed version, and the file that declares it.
3. Check for existing overrides, pins, constraints and ignore files. Earlier fixes live there and may now be stale.
4. Open the reference for the ecosystem: [Java](references/java.md) (Maven, Gradle) or [Python](references/python.md) (pip, uv, Poetry).

## Workflow

1. **Baseline.** Run the build and tests, and the scanner if available, before changing anything. Record what passes and the list of findings.
2. **Confirm each finding.** Check the installed version against the advisory's affected range. Scanners report false matches, especially for shaded, vendored or renamed packages.
3. **Trace the path.** For each vulnerable package, produce the dependency path from a direct dependency down to it. Note whether it is direct or transitive, and whether it is a runtime, build-only or test-only dependency.
4. **Group by fix.** Several findings often share one parent. Find upgrades that clear the most findings per change.
5. **Choose the fix** for each group using the order below.
6. **Check the upgrade.** Note whether it crosses a major version. Read the changelog or release notes for breaking changes, and search the code for the APIs they mention.
7. **Apply one group at a time.** Change the manifest, regenerate the lockfile with the package manager, and never hand-edit a lockfile.
8. **Verify.** Rebuild, run the tests, and rescan. Confirm the resolved version in the dependency tree is the one intended and that no new finding was introduced.
9. **If it breaks,** fix the call sites when the change is small and clear. Otherwise revert that group and report it as needing a decision.
10. **Report** as described at the end.

## Choosing the fix

Prefer the first option that works:

1. **Upgrade the direct dependency** to the lowest version that fixes the advisory. The lowest fixing version carries the least risk of unrelated breakage.
2. **For a transitive finding, upgrade the parent** to a version that pulls in a fixed child. This keeps versions that were tested together.
3. **Force the transitive version** with the ecosystem's override mechanism when no parent release fixes it. Add a comment with the advisory identifier and the condition for removing the override. Stay within the same major version of the child where possible.
4. **Remove or replace the dependency** when it is unmaintained or the code using it is trivial.
5. **No fix available:** check whether the vulnerable function is used at all. Record the finding with the reason, any mitigation, and a date to revisit. Use the scanner's own ignore mechanism, scoped to that advisory, with an expiry.

## Judging whether a finding applies

A finding can be recorded as not affecting the project only with evidence:

- The package is test-only or build-only and never ships. State how you know.
- The vulnerable function or module is never imported or called. Show the search.
- The vulnerable code path needs a configuration or feature the project does not enable.

Never mark a finding as not applicable because the fix is inconvenient. If unsure, treat it as applicable.

## Risk notes

- Major-version upgrades, framework upgrades and anything touching serialisation, authentication or cryptography libraries need explicit review. Flag them; do not bundle them with routine bumps.
- Overrides rot. An override that outlives its reason silently holds a package back later. Remove ones that are no longer needed while you are there, and say which.
- A newer version can carry its own advisories. Always rescan after the change.
- Do not combine security fixes with unrelated dependency updates in the same change.

## Do not

- Hand-edit a lockfile, or delete it to "start clean".
- Upgrade everything to latest to clear a few findings.
- Suppress, ignore or lower the severity of a finding without recorded evidence and an expiry.
- Leave an override without a comment saying why it exists.
- Disable a failing test or security gate to get the change through.
- Report a finding as fixed without a rescan. If no scanner is available here, say so, show the resolved version against the advisory's fixed version, and give the scan command.

## Report

For each finding: advisory identifier, package, old and new resolved version, the fix type used (direct upgrade, parent upgrade, override, removal, recorded exception), and the dependency path. Then: build, test and rescan commands with results; breaking changes handled; overrides added or removed; findings left open, with reason and next step.

Sources for these rules are in [references/sources.md](references/sources.md).
