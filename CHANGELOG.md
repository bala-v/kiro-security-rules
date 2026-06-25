# Changelog

All notable changes to kiro-security-rules will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Conditional steering `fileMatchPattern`** — `auth-framework-patterns.md` and `package-ecosystem-security.md` now declare `fileMatchPattern` as a YAML array instead of a single comma-separated string, so Kiro actually matches the patterns and loads these files.
- **Unsupported `onStartup` hook trigger** — `auto-validate-rules.json` now uses the supported `preToolUse` trigger (first file write of a session) instead of the undocumented `onStartup`. `kiro-security-check validate` is elevated as the canonical install verification step.
- **SBOM hook scope** — `verify-sbom-exists.json` no longer fires on every shell command. It now validates the SBOM only when `sbom.spdx.json` is edited. Pre-push SBOM/audit/secret enforcement moved to a CI/CD template (`ci/pre-push-checks.yml`).
- **Supply-chain risk in dependency audit hook** — `dependency-audit-on-change.json` no longer uses `npx` (which executes unverified remote code). It now uses locally installed tools only (`npm audit`, `pip-audit`, `poetry audit`, `cargo audit`, `bundler-audit`, `govulncheck`) and fails loudly (exit 1) when none is found.
- **Logging compliance scope** — `logging-standards.md` annotates PII/PHI prohibitions with their compliance frameworks (GDPR, HIPAA, CCPA, PCI-DSS) and documents the workspace-level override pattern for teams in other regulatory contexts.
- **Template misload risk** — removed `templates/custom-security-rule.md.example` (a `.md` file with front-matter that could be mistakenly loaded as steering). The template now lives in the README "Creating Custom Security Rules" section.

### Changed
- **Slimmed always-on steering files** — the four always-on files are now ≤40 lines each (policy statements only). Detailed pattern tables, command references, and anti-pattern matrices moved to the relevant conditional and manual/auto workflows.
- **Single source of truth for enforcement patterns** — `secrets-management.md` and `supply-chain-security.md` no longer duplicate the credential patterns / audit commands owned by their hooks; they state policy intent and reference the authoritative hook. Both enforcement hooks gained a `_note` marking them authoritative.
- **`install.sh` / postinstall** — now print a prominent prompt to generate the Kiro foundational steering files (`product.md`, `tech.md`, `structure.md`) and surface `kiro-security-check validate` as the primary verification step.

### Added
- **Foundational steering templates** (`templates/foundational/`) — fill-in-the-blank `product.md`, `tech.md`, and `structure.md` starters, each with `inclusion: always` front-matter, `[PLACEHOLDER]` markers, and concise `<!-- INSTRUCTIONS -->` blocks. `install.sh` gained an opt-in `--with-templates` flag that no-clobber copies them into `.kiro/steering/`; the default still prefers Kiro's IDE "Generate Steering Docs" generator since it analyses the actual codebase. README Quick Start documents when to use each path.
- **Team & enterprise adoption guide** (`docs/adoption-guide.md`) — covers Kiro steering distribution (global vs. workspace), three adoption tiers (individual, small team, enterprise MDM), the override model, CI/CD integration, a 4-week rollout playbook, and adoption metrics. Includes three syntax-validated MDM deployment scripts (Jamf postinstall bash, Intune PowerShell, Group Policy batch), each with SHA256 integrity verification, no-overwrite copying, and a `~/.kiro/.security-rules-version` sentinel.
- **Compliance overlay placeholders** (`overlays/`) — `pci-dss-overlay.md`, `hipaa-overlay.md`, `sox-overlay.md`, and `internal-tools-lite.md`, each with `inclusion: always` front-matter, for layering regulatory rules on top of the baseline.
- **CI workflow example** (`docs/examples/security-baseline.yml`) — Gitleaks full-history secret scan, lockfile-conditional dependency audits (npm/pip-audit/cargo), SBOM (SPDX 2.3+) validation, and an optional Kiro rules version gate.
- **README Quick Start router** — restructured to route individual, small-team, and enterprise/fleet adopters to the appropriate tier in the adoption guide.
- **`auto` inclusion mode** — `sbom-generation.md` and `log-review.md` converted from `manual` to `auto`; Kiro loads them automatically when the conversation matches their description, while they remain available as slash commands. `security-audit.md` stays `manual`.
- **MCP configuration** (`mcp/mcp.json`) — `fetch` (live OWASP/NVD/OSV queries) and `awslabs.aws-documentation-mcp-server`. Installed to `.kiro/settings/mcp.json` by all install paths (no overwrite). Always-on steering files reference MCP for live CVE lookups.
- **CI/CD template** (`ci/pre-push-checks.yml`) — GitHub Actions workflow for pre-push SBOM existence/format validation and dependency audits.

## [1.0.0] — 2026-06-14

### Added

#### Always-On Steering Rules
- `secrets-management.md` — Prohibits hardcoded secrets, credentials, API tokens, PAT tokens. Recognizes 15+ credential patterns (AWS, GitHub, Stripe, Google, Slack, JWT, private keys, connection strings). Mandates env variable usage with pre-write and pre-commit checks.
- `supply-chain-security.md` — Zero tolerance for critical/high CVEs. Requires all dependencies declared in build files with committed lock files. Mandates SPDX 2.3+ SBOM at repository root.
- `authentication-standards.md` — Mandates OAuth 2.0 / OIDC with Authorization Code + PKCE. Prohibits Implicit and ROPC flows. Requires MFA for admin operations. Token handling rules (httpOnly cookies, short lifetimes, rotation).
- `logging-standards.md` — Structured JSON logging with 11 required fields. Prohibits PII and PHI in logs. Mandates audit logging for auth, authorization, and data mutation events.

#### Conditional Steering Rules
- `package-ecosystem-security.md` — File-matched on build/lock files. Ecosystem-specific audit commands and SBOM generation for Node.js, Python, Rust, Go, Ruby, Java.
- `auth-framework-patterns.md` — File-matched on auth-related filenames. Framework-specific patterns for Express/Passport, Django/FastAPI, Spring Boot.

#### Manual Steering Workflows
- `#security-audit` — 5-phase audit covering secrets, supply chain, auth, logging, dependencies.
- `#sbom-generation` — Step-by-step SBOM generation workflow per ecosystem.
- `#log-review` — 4-phase log audit for PII/PHI, format compliance, auth events, sensitive data.

#### Agent Hooks
- `pre-write-secret-scan.json` — Scans file content before write for hardcoded secrets.
- `dependency-audit-on-change.json` — Runs vulnerability audit when build files change.
- `verify-sbom-exists.json` — Verifies SBOM exists before git push.
- `auto-validate-rules.json` — Validates always-on rules on Kiro startup.

#### CLI & Distribution
- `kiro-security-check` CLI with `validate`, `status`, `update`, `audit` commands.
- Python pip package (`pyproject.toml`) with post-install rule deployment.
- Node.js npm package (`package.json`) with postinstall script.
- `scripts/bundle.sh` — Creates distributable .tar.gz and .zip artifacts.
- `scripts/ci-deploy.sh` — CI/CD integration for automated rule deployment.
- `scripts/postinstall.js` — npm postinstall rule installer.
- `templates/custom-security-rule.md.example` — Template for company-policy-specific rules with compliance framework mapping (SOC 2, PCI-DSS, HIPAA).
- `install.sh` — Traditional shell installer with `--global` flag.
- Comprehensive test suite: 5 test modules covering always-on rules, steering format, hooks format, secret patterns, and install verification.
