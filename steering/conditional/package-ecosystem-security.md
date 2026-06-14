---
inclusion: fileMatch
fileMatchPattern: "**/package.json, **/requirements.txt, **/poetry.lock, **/Cargo.toml, **/Cargo.lock, **/Gemfile, **/Gemfile.lock, **/go.mod, **/go.sum, **/pyproject.toml, **/pom.xml, **/build.gradle, **/yarn.lock, **/pnpm-lock.yaml"
---

# Package Ecosystem Security

This rule activates when a build, package, or lock file is opened. Follow the ecosystem-specific audit procedure below.

## Node.js (package.json, yarn.lock, pnpm-lock.yaml)

```bash
# Audit for vulnerabilities
npm audit --audit-level=high

# If using yarn
yarn audit --level high

# If using pnpm
pnpm audit --audit-level=high

# Fix automatically (when possible)
npm audit fix --audit-level=high
```

Critical/high findings MUST be resolved before commit. If no fix is available, the dependency must be replaced or a security exception filed.

## Python (requirements.txt, pyproject.toml, poetry.lock)

```bash
# Using pip-audit
pip install pip-audit
pip-audit

# Using poetry
poetry audit

# Using pip
pip install safety
safety check
```

## Rust (Cargo.toml, Cargo.lock)

```bash
# Install cargo-audit
cargo install cargo-audit

# Audit
cargo audit
```

## Go (go.mod, go.sum)

```bash
# Built-in vulnerability check
go list -m -json all | go run golang.org/x/vuln/cmd/govulncheck@latest
```

## Ruby (Gemfile, Gemfile.lock)

```bash
# Using bundler-audit
gem install bundler-audit
bundler-audit check --update
```

## Java (pom.xml, build.gradle)

```bash
# Using OWASP Dependency-Check
mvn org.owasp:dependency-check-maven:check

# Using Gradle plugin
gradle dependencyCheckAnalyze
```

## SBOM Generation Per Ecosystem

```bash
# Node.js
npx @cyclonedx/bom --output sbom.spdx.json

# Python
pip-licenses --format=json --output-file=sbom.spdx.json

# Rust
cargo install cargo-cyclonedx
cargo cyclonedx

# Go
go install github.com/spdx/tools-golang/builder@latest
# or use syft
syft . -o spdx-json=sbom.spdx.json
```

## Pre-Commit Checklist for Dependency Changes

- [ ] Vulnerability audit passes (zero critical, zero high)
- [ ] All dependencies declared in build manifest
- [ ] Lock file updated and committed
- [ ] SBOM regenerated and valid
- [ ] No deprecated packages added
- [ ] License compatibility verified
