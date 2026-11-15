# Sources: sca-fixes

Most of these were seen as search-result excerpts rather than read in full. Treat the cited figures as directional.

| Rule in this skill | Source | How it was used |
| --- | --- | --- |
| The fix is an upgrade to a version someone else patched; transitive findings must be traced to a dependency the project controls and the whole chain checked | [Pixee: SCA Remediation at Scale](https://www.pixee.ai/blog/sca-remediation-at-scale-dependencies-real-challenge) | Search excerpt; paraphrased |
| Most vulnerabilities sit in transitive dependencies; separate handling for direct and transitive; check API compatibility and cascading effects before merging | [Endor Labs: SCA remediation](https://www.endorlabs.com/learn/sca-remediation) | Search excerpt; paraphrased |
| Check whether the vulnerable function is reachable before prioritising | Both of the above | Search excerpt; basis for "judging whether a finding applies" |
| Version bumps without breaking-change analysis are the reason automated fix PRs go unmerged | [Pixee: Breaking change detection](https://www.pixee.ai/resource-center/software-supply-chain-security/breaking-change-detection) | Search excerpt; basis for the upgrade-check step |
| Upgrade to the minimum patched version to limit breakage | [AppSec Santa: Dependabot](https://appsecsanta.com/dependabot), describing Dependabot's behaviour | Search excerpt |
| Group fixes by how many vulnerabilities one upgrade resolves; strategies of in-place lock update, relock and override | [OSV-Scanner: Guided remediation](https://google.github.io/osv-scanner/experimental/guided-remediation) | Search excerpt of the documentation page |
| Overrides go stale: orphaned targets, pins the tree has moved past, ineffective nested overrides | [OWASP cve-lite-cli](https://github.com/owasp/cve-lite-cli) | Search excerpt; basis for "overrides rot" |
| Taking a dependency is a lasting commitment | [Software Engineering at Google, ch. 21](https://abseil.io/resources/swe-book/html/ch21.html) | Search excerpt |
| Verify by build, tests and rescan before calling a fix done | [Snyk: Remediation Agent](https://docs.snyk.io/scan-fix-and-prevent/fix/remediation-agent), which describes scan, plan, fix, verify | Search excerpt; the workflow shape is common practice |

From general engineering knowledge, not a cited source: the ordering of fix options, the evidence required to record a finding as not applicable, the risk notes, and every command, flag and configuration snippet in the reference files. The uv commands (`uv tree --invert --package`, `uv lock --upgrade-package`, `constraint-dependencies`) and the pip-audit and pipdeptree flags were run against a small sample project while building this repository. The npm commands (`npm ls`, `npm explain`, `npm update`, `npm audit --omit=dev`, `npm ci`) and a nested `overrides` entry were also run against a sample project. The Maven, Gradle (including version catalogs, Android and Multiplatform configurations, and dependency verification), pnpm, Yarn, Poetry, pip-tools and OSV-Scanner commands were not executed; verify them against the tool versions in use.
