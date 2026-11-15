# SCA fixes: Kotlin

Kotlin projects on the JVM and Android build with Gradle, usually with the Kotlin DSL, so the commands and fix options in the [Java reference](java.md) apply directly: `dependencyInsight` to trace, upgrade the direct dependency or parent first, then a `constraints` block, then an exclusion. This file covers what is specific to Kotlin and Android builds.

## Where versions are declared

Check all of these before editing; a finding can originate in any of them.

| Location | What lives there |
| --- | --- |
| `gradle/libs.versions.toml` | The version catalog. Most modern Kotlin builds declare versions here. |
| `build.gradle.kts` in each module | Dependencies, sometimes with inline versions. |
| `buildSrc/` or `build-logic/` | Convention plugins that add dependencies and constraints to many modules. |
| `settings.gradle.kts` | Plugin versions and repositories. |
| A platform or BOM module | Shared constraints, if the project has one. |

Upgrade in the version catalog when the dependency is declared there:

```toml
[versions]
# GHSA-xxxx-xxxx-xxxx: fixed in 2.4.1
vulnerable-lib = "2.4.1"

[libraries]
vulnerable-lib = { module = "com.example:vulnerable-lib", version.ref = "vulnerable-lib" }
```

A catalog entry only declares an alias. It does not force a transitive version; for that, use a constraint.

## Forcing a transitive version

```kotlin
dependencies {
    constraints {
        implementation("com.example:vulnerable-lib:2.4.1") {
            because("GHSA-xxxx-xxxx-xxxx; transitive via parent-lib. Remove when parent-lib >= 5.2.")
        }
    }
}
```

In a multi-module build, put the constraint in the shared convention plugin or platform module so every module resolves the same version. Adding it to one module leaves the others vulnerable.

## Tracing

```bash
./gradlew :app:dependencyInsight --dependency vulnerable-lib --configuration runtimeClasspath
```

Configurations differ by project type:

| Project | Configuration that ships |
| --- | --- |
| JVM | `runtimeClasspath` |
| Android | per variant, for example `releaseRuntimeClasspath` |
| Kotlin Multiplatform | per target, for example `jvmRuntimeClasspath`, `iosArm64MainImplementation` |

Check the release variant on Android; a finding only in `debugRuntimeClasspath` or a test configuration does not ship, though it still runs on developer machines and CI.

## Linked versions

Several Kotlin library families must move together. Override them through their BOM or shared version, not one artifact at a time:

- **Kotlin standard library** and the Kotlin Gradle plugin. The stdlib version follows the plugin; do not pin `kotlin-stdlib` separately from it.
- **kotlinx.coroutines**, **kotlinx.serialization** and **Ktor**, each of which publishes a BOM. Their releases are also tied to minimum Kotlin versions.
- **Compose** compiler and runtime, tied to the Kotlin version.
- **AndroidX** groups such as lifecycle, navigation and room.
- **OkHttp** and **Okio**, common transitive findings on Android.

An upgrade that requires a newer Kotlin version is a toolchain upgrade, not a dependency bump. Report it for a decision.

## Compiler plugins and annotation processors

KSP and kapt processors, and Gradle plugins themselves, are build-time dependencies. A finding there is exposure in the build environment, not in the shipped artifact. Fix by upgrading the plugin or processor; record the distinction in the report. KSP versions are tied to the Kotlin version.

## Kotlin Multiplatform

Dependencies are declared per source set, and a vulnerable package may be present for one target only. Trace each target's configuration, fix in the source set that declares it (often `commonMain`), and verify every target still resolves and compiles.

## Android specifics

- Scanners may flag libraries inside an AAR that the dependency tree shows only by the AAR's coordinates. Upgrade the AAR.
- Google Play Services and Firebase are managed through their BOM; upgrade the BOM.
- An upgrade may raise the minimum SDK or require a newer Android Gradle Plugin. Check the release notes before applying.
- Verify with the release build, not only debug: `./gradlew :app:assembleRelease` and the unit tests for that variant.

## Locking and verification

If `gradle.lockfile` files exist, regenerate with `./gradlew dependencies --write-locks`. If the project uses dependency verification (`gradle/verification-metadata.xml`), regenerate that as well with `./gradlew --write-verification-metadata sha256 help`, and review the diff rather than accepting it blindly.

```bash
./gradlew :app:dependencyInsight --dependency vulnerable-lib --configuration runtimeClasspath
./gradlew check
```

Then rescan with the scanner the project's pipeline uses.
