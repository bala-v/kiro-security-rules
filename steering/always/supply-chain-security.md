---
inclusion: always
---

# Supply Chain Security

> For live CVE lookups and advisories, use the `fetch` MCP: ask Kiro to "look up CVE-YYYY-NNNNN on NVD" or "check OSV for GHSA-XXXX."

## Vulnerability Auditing

Zero critical and zero high CVEs before any release. The dependency audit hook (`hooks/dependency-audit-on-change.json`) runs automatically on every dependency file change using your locally installed audit tool, and is the authoritative source for which audit commands run per ecosystem.

For manual audits or release checks: run `#security-audit` Phase 2 and Phase 5.

## Dependency Declaration

All dependencies must be declared in build manifests with pinned versions. Lock files (`package-lock.json`, `poetry.lock`, `Cargo.lock`, `go.sum`, `Gemfile.lock`, etc.) must be committed to version control. Removing a dependency must also remove it from the build file.

## SBOM

An SBOM in SPDX 2.3+ format must exist at `sbom.spdx.json` (single repo) or `sbom/<component>.spdx.json` (monorepo). It must cover all direct and transitive dependencies with versions and licenses, and be regenerated whenever dependencies change.

Run `#sbom-generation` for ecosystem-specific generation and validation steps.
