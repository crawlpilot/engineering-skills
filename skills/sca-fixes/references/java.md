# SCA fixes: Java (Maven and Gradle)

Commands and syntax are for current Maven 3 and Gradle 8 conventions. Check them against the project's build tool version, and use the wrapper (`./mvnw`, `./gradlew`) when the project has one. Coordinates and versions below are placeholders.

## Maven

### Trace the path

```bash
mvn dependency:tree -Dincludes=com.example:vulnerable-lib
mvn dependency:tree -Dverbose -Dincludes=com.example:vulnerable-lib   # shows omitted conflicts
mvn help:effective-pom | less                                          # where a managed version comes from
```

The tree shows each path from a direct dependency. Note the scope: `test` and `provided` do not ship in the artifact.

### Fix options, in order

**1. Upgrade the direct dependency** in `<dependencies>`, or its version property.

**2. Upgrade the parent** that brings the vulnerable artifact in. Check which parent release resolves a fixed child:

```bash
mvn versions:display-dependency-updates
```

**3. Version managed by a BOM or parent POM** (common with Spring Boot). Prefer bumping the BOM or parent. If the BOM exposes a version property, override that property:

```xml
<properties>
  <!-- GHSA-xxxx-xxxx-xxxx: remove once the parent BOM ships >= 2.4.1 -->
  <vulnerable-lib.version>2.4.1</vulnerable-lib.version>
</properties>
```

**4. Force a transitive version** with `dependencyManagement`. This sets the version wherever the artifact appears, without adding it as a direct dependency:

```xml
<dependencyManagement>
  <dependencies>
    <!-- GHSA-xxxx-xxxx-xxxx: transitive via com.example:parent-lib. Remove when parent-lib >= 5.2 is adopted. -->
    <dependency>
      <groupId>com.example</groupId>
      <artifactId>vulnerable-lib</artifactId>
      <version>2.4.1</version>
    </dependency>
  </dependencies>
</dependencyManagement>
```

In a multi-module build, put this in the parent POM so every module resolves the same version.

**5. Exclude** the artifact when the parent does not need it at runtime, then confirm nothing fails with `ClassNotFoundException`:

```xml
<exclusions>
  <exclusion>
    <groupId>com.example</groupId>
    <artifactId>vulnerable-lib</artifactId>
  </exclusion>
</exclusions>
```

### Verify

```bash
mvn dependency:tree -Dincludes=com.example:vulnerable-lib   # resolved version is the intended one
mvn verify
```

## Gradle

### Trace the path

```bash
./gradlew dependencyInsight --dependency vulnerable-lib --configuration runtimeClasspath
./gradlew dependencies --configuration runtimeClasspath
```

`dependencyInsight` shows every path and why a version was selected. Check `runtimeClasspath` for what ships and `testRuntimeClasspath` for test-only findings. In multi-project builds, prefix the task with the project path.

### Fix options, in order

**1. Upgrade the direct dependency**, in the build file or the version catalog (`gradle/libs.versions.toml`) if the project uses one.

**2. Upgrade the parent**, or the platform or BOM that manages the version.

**3. Force a transitive version with a constraint.** A constraint applies only if the artifact is already in the graph:

```kotlin
dependencies {
    constraints {
        implementation("com.example:vulnerable-lib:2.4.1") {
            because("GHSA-xxxx-xxxx-xxxx; transitive via parent-lib. Remove when parent-lib >= 5.2.")
        }
    }
}
```

Use a `strictly` version or `resolutionStrategy.force` only when a constraint is overridden by another rule, and say why. Where a shared convention plugin or platform project exists, put the constraint there.

**4. Exclude** when the parent does not need it at runtime:

```kotlin
implementation("com.example:parent-lib:5.1.0") {
    exclude(group = "com.example", module = "vulnerable-lib")
}
```

### Lockfiles

If the project uses dependency locking (`gradle.lockfile` files exist), regenerate them with Gradle and commit the result:

```bash
./gradlew dependencies --write-locks
```

Never edit a lockfile by hand.

### Verify

```bash
./gradlew dependencyInsight --dependency vulnerable-lib --configuration runtimeClasspath
./gradlew check
```

## Scanning

Use the scanner the project or its pipeline already uses, so results match the gate. If none is configured, OSV-Scanner is a free option:

```bash
osv-scanner scan -r .
osv-scanner fix -M pom.xml          # experimental guided remediation; Maven manifests
```

Review whatever a guided-remediation tool proposes like any other change, and rerun the build and tests.

## Java-specific cautions

- **Shaded and fat jars.** A vulnerable class can be bundled inside another artifact under a relocated package. Dependency trees will not show it; only upgrading the bundling artifact fixes it. Scanners also sometimes flag the wrong coordinates for shaded code.
- **Version conflicts.** Maven picks the nearest declaration, not the highest version, so a new override can silently downgrade another path. Gradle picks the highest by default. Always check the resolved tree after the change.
- **Linked versions.** Families such as Jackson, Netty, Log4j and Spring modules must move together. Override through the family's BOM or shared property, not one artifact.
- **Major upgrades.** Namespace changes (for example `javax` to `jakarta`) and logging or serialisation library majors are migrations, not version bumps. Report them for a decision.
- **Build plugins.** Findings in Maven or Gradle plugins are build-time exposure, not shipped code. Fix by upgrading the plugin; record the distinction.
