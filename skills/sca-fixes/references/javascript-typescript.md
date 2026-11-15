# SCA fixes: JavaScript and TypeScript (npm, pnpm, Yarn)

Identify the package manager from the lockfile and use only that one. Running a different manager creates a second lockfile and a different dependency tree. Flags vary between versions; check `--help` when a command is rejected. Package names and versions below are placeholders.

| Lockfile | Manager | Also check |
| --- | --- | --- |
| `package-lock.json` | npm | `packageManager` field in `package.json` |
| `pnpm-lock.yaml` | pnpm | `pnpm-workspace.yaml` |
| `yarn.lock` | Yarn | `.yarnrc.yml` means Yarn 2 or later; its absence usually means Yarn 1 |

In a workspace or monorepo, run commands from the root unless the project documents otherwise, and check every workspace's manifest.

## Trace the path

```bash
npm ls vulnerable-lib            # every path to it
npm explain vulnerable-lib       # why each copy is installed
pnpm why vulnerable-lib
yarn why vulnerable-lib
```

Several versions of the same package can be installed at once. Fix every vulnerable copy, not just the first one listed. Note whether each path starts from `dependencies` or `devDependencies`; dev-only packages do not ship in a production build, but they run on developer machines and in CI, and build tools can affect the shipped bundle.

## Fix options, in order

### 1. Upgrade the direct dependency

```bash
npm install vulnerable-lib@^2.4.1
pnpm add vulnerable-lib@^2.4.1
yarn add vulnerable-lib@^2.4.1        # Yarn 1: same; Yarn 2+: yarn up vulnerable-lib@^2.4.1
```

### 2. Transitive: update within existing ranges

Often the parent's range already allows the fixed version and only the lockfile is stale. Update just that package:

```bash
npm update vulnerable-lib
pnpm update vulnerable-lib --depth Infinity
yarn up -R vulnerable-lib              # Yarn 2+
```

This changes only the lockfile. Try it first for transitive findings. `npm audit fix` (without `--force`) does the same across all findings and is reasonable when the resulting diff is small and reviewed.

### 3. Transitive: upgrade the parent

If the parent's range excludes the fixed version, upgrade the parent to a release that allows it.

### 4. Force the transitive version

When no parent release allows the fix, use the manager's override mechanism. Add the advisory identifier and removal condition in the commit message and in the project's dependency notes, since `package.json` cannot hold comments.

npm, in `package.json`:

```json
{
  "overrides": {
    "vulnerable-lib": "^2.4.1"
  }
}
```

Scope it to one parent when only that path needs it:

```json
{
  "overrides": {
    "parent-lib": {
      "vulnerable-lib": "^2.4.1"
    }
  }
}
```

pnpm, in `package.json` (newer pnpm versions also accept `overrides` in `pnpm-workspace.yaml`; follow where the project already keeps its settings):

```json
{
  "pnpm": {
    "overrides": {
      "vulnerable-lib": "^2.4.1",
      "parent-lib>vulnerable-lib": "^2.4.1"
    }
  }
}
```

Yarn, in `package.json`:

```json
{
  "resolutions": {
    "vulnerable-lib": "^2.4.1"
  }
}
```

After editing, run the manager's install so the lockfile is regenerated. In a workspace, overrides and resolutions take effect only in the root `package.json`.

Stay within the major version the parent was written against. Forcing a new major onto a parent that expects the old one moves the breakage to runtime, where the type checker will not see it.

### 5. Remove or replace

Many small packages duplicate what the platform now provides. If the vulnerable package is trivial or unmaintained, removing it or its parent is often the cleanest fix.

## Verify

```bash
npm ls vulnerable-lib            # every resolved copy is at or above the fixed version
npm ci && npm run build && npm test
```

Use the clean-install command (`npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable` or `--frozen-lockfile`) to prove the lockfile and manifest agree. Run the type check and the production build as well as the tests; a transitive change can break bundling without failing a unit test.

## Scanning

Use the scanner the project or its pipeline already uses, so results match the gate. Built-in and free options:

```bash
npm audit                        # also: pnpm audit, yarn npm audit (Yarn 2+), yarn audit (Yarn 1)
npm audit --omit=dev             # production dependencies only
osv-scanner scan -r .
```

## Cautions specific to this ecosystem

- **`npm audit fix --force` is not a routine command.** It installs breaking major versions and can downgrade packages. Do not run it without reading what it will change.
- **Never delete the lockfile to "refresh" it.** That re-resolves every dependency at once and turns a targeted fix into an unreviewable change.
- **Overrides rot.** They stay in force after the parent catches up and can later hold a package back or mask a conflict. List existing overrides, and remove any whose reason has expired.
- **Peer dependencies.** An override can violate a peer range. Read install warnings after the change.
- **Dev-tool findings.** Many advisories in build and test tooling concern a development server or input the project never feeds it. Record these with evidence rather than forcing risky upgrades, and still fix them when the fix is cheap.
- **Bundled dependencies.** Some packages ship their own copies inside the tarball. No override reaches those; only upgrading the bundling package does.
- **Install scripts.** A new or changed package version can run arbitrary code at install time. Be cautious with a version published very recently, and prefer one that has been available for some days unless the advisory is urgent.
- **Runtime support.** A fixed release may require a newer Node.js version than the project runs. Check the `engines` field before upgrading.
- **ESM-only majors.** Several popular packages dropped CommonJS in a major release. Crossing that boundary is a migration to report, not a bump.
