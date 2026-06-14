# Kiro Security Steering Rules

**Enterprise security policies encoded as Kiro AI agent steering rules.** Always-on, conditional, and on-demand rules that enforce your organization's security standards across every project team.

Built by the central security team for distribution to all engineering teams using [Kiro IDE](https://kiro.dev).

Follows the steering file conventions from [everything-kiro](https://github.com/yuening8080/everything-kiro) — three inclusion tiers (`always`, `conditional`, `manual`) with YAML frontmatter, plus agent hooks for IDE event automation. These rules are designed to be installed alongside your project's existing steering files (product, tech, structure) from everything-kiro.

---

## Quick Start

### Option 1: pip install (recommended for Python teams)

```bash
pip install git+https://github.com/your-org/kiro-steering-rules.git
kiro-security-check validate
```

### Option 2: npm install (recommended for Node.js teams)

```bash
npm install git+https://github.com/your-org/kiro-steering-rules.git
kiro-security-check validate
```

### Option 3: Shell installer (any project)

```bash
git clone git@github.com:your-org/kiro-steering-rules.git
cd kiro-steering-rules
./install.sh /path/to/your/project

# Or install globally (all projects on this machine)
./install.sh --global
```

### Option 4: Git submodule (track updates from security team)

```bash
git submodule add git@github.com:your-org/kiro-steering-rules.git .kiro-rules
.kiro-rules/install.sh .

# Later, pull updates:
git submodule update --remote .kiro-rules
.kiro-rules/install.sh .
```

---

## Security Policies

### Always-On Rules (loaded in every Kiro conversation)

| Rule | Policy | Enforcement |
|------|--------|-------------|
| `secrets-management.md` | No hardcoded secrets, credentials, API tokens, or PAT tokens in source code | Pre-write scan + pre-commit check |
| `supply-chain-security.md` | Zero critical/high CVEs, all deps in build files, SPDX SBOM in repo root | Audit on dep change + pre-push SBOM check |
| `authentication-standards.md` | OAuth 2.0 / OIDC required, Authorization Code + PKCE, MFA for admin | Code review + architecture review |
| `logging-standards.md` | Structured JSON logs, no PII/PHI in logs, audit trail required | Log review + code review |

### Conditional Rules (activated by file type)

| Rule | Triggers On | What It Enforces |
|------|-------------|------------------|
| `package-ecosystem-security.md` | `package.json`, `requirements.txt`, `poetry.lock`, `Cargo.toml`, `go.mod`, etc. | Ecosystem-specific audit commands + SBOM generation |
| `auth-framework-patterns.md` | `*auth*`, `*login*`, `*oauth*`, `*jwt*`, `*token*`, `*session*`, `*middleware*` | Framework-specific OIDC patterns for Express, Django, Spring Boot |

### Manual Workflows (activate with `#name` in Kiro chat)

| Command | Purpose |
|---------|---------|
| `#security-audit` | Full 5-phase audit: secrets, supply chain, auth, logging, dependencies |
| `#sbom-generation` | Generate SPDX SBOM for the current project |
| `#log-review` | Audit logs for PII/PHI exposure and format compliance |

---

## CLI Tool

```bash
kiro-security-check validate   # Check all always-on rules are present
kiro-security-check status     # Show current installation state
kiro-security-check update     # Pull latest rules from package registry
kiro-security-check audit      # Run full compliance audit
kiro-security-check --json     # Output in JSON format (for CI integration)
```

---

## For Security Team Leads

### Publishing Updates

1. Make changes to steering rules, hooks, or templates
2. Update `CHANGELOG.md` and bump version in `pyproject.toml` and `package.json`
3. Tag a release: `git tag v1.1.0 && git push --tags`
4. GitHub Actions will auto-build artifacts and create a release
5. Teams pull updates via `kiro-security-check update` or `git submodule update`

### Distribution Flow

```
Security team pushes to main
       ↓
GitHub Actions: lint → test → bundle → release
       ↓
Release artifacts published (.tar.gz, .zip, pip, npm)
       ↓
Project teams: kiro-security-check update OR submodule pull
```

### Adding a New Policy

1. Create a new `.md` file in `steering/always/` (or `conditional/`, `manual/`)
2. Add YAML frontmatter with `inclusion: always`
3. Add tests in `tests/test_always_on_rules.py`
4. Update `CHANGELOG.md`
5. Tag a release

---

## For Project Teams

### Verifying Installation

```bash
kiro-security-check validate
```

Expected output:
```
[PASS] secrets-management.md
[PASS] supply-chain-security.md
[PASS] authentication-standards.md
[PASS] logging-standards.md
[PASS] No secrets found in diff
[PASS] SBOM found at sbom.spdx.json (SPDX-2.3)
```

### Checking for Updates

```bash
kiro-security-check status   # Shows current version
kiro-security-check update   # Pulls latest from security team
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Validate Kiro Security Rules
  run: kiro-security-check validate
```

```yaml
- name: Deploy Latest Security Rules
  run: curl -sL https://github.com/your-org/kiro-steering-rules/releases/latest/download/bundle.sh | bash
```

---

## Custom Rules

Use `templates/custom-security-rule.md.example` to create organization-specific rules:

```bash
cp templates/custom-security-rule.md.example steering/always/my-company-policy.md
```

The template includes:
- YAML frontmatter for Kiro integration
- Compliance framework mapping (SOC 2, PCI-DSS, HIPAA)
- Implementation checklist
- Test plan
- Remediation guidance

---

## Steering File Format

Every steering file follows the [everything-kiro](https://github.com/yuening8080/everything-kiro) convention:

```yaml
---
inclusion: always          # always | fileMatch | manual
fileMatchPattern: "*.py"   # only required for fileMatch inclusion
---

# Rule Content
```

This format is compatible with all steering files generated by everything-kiro's foundation generator (`product.md`, `tech.md`, `structure.md`).

---

## Project Structure

```
kiro-steering-rules/
├── steering/
│   ├── always/                  # Loaded in every Kiro conversation
│   ├── conditional/             # Loaded when matching files are opened
│   └── manual/                  # Activated on-demand with #name
├── hooks/                       # Kiro agent automation hooks
├── templates/                   # Custom rule templates
├── src/kiro_security/           # Python CLI & validator
├── tests/                       # Test suite
├── scripts/                     # Bundle and CI/CD helpers
├── install.sh                   # Shell installer
├── pyproject.toml               # Python package
├── package.json                 # Node.js package
├── CHANGELOG.md
└── README.md
```

---

## Development

```bash
# Install in dev mode
pip install -e .

# Run tests
pytest tests/ -v

# Bundle for distribution
bash scripts/bundle.sh
```

## Acknowledgements

- **[everything-kiro](https://github.com/yuening8080/everything-kiro)** — The steering file anatomy, inclusion modes (`always`, `fileMatch`, `manual`), and agent hook patterns used throughout this project are adapted from everything-kiro's production-ready Kiro optimization system. The security rules here are designed to complement everything-kiro's foundational steering files (product, tech, structure).
- **[Project CodeGuard](https://github.com/cosai-oasis/project-codeguard)** — An OASIS/CoSAI open standard for AI coding agent security rules. Our secret detection patterns, input validation guidance, and authentication standards are informed by CodeGuard's comprehensive rule set.

## License

MIT
