# Changelog

All notable changes to kiro-security-rules will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
