# Kiro Security Steering Rules

**Enterprise security policies encoded as Kiro AI agent steering rules.** Always-on, conditional, and on-demand rules that enforce your organization's security standards across every project team.

Built by the central security team for distribution to all engineering teams using [Kiro IDE](https://kiro.dev).

Follows the steering file conventions from [everything-kiro](https://github.com/yuening8080/everything-kiro) — inclusion tiers (`always`, `conditional`/`fileMatch`, `auto`, `manual`) with YAML frontmatter, plus agent hooks for IDE event automation and MCP servers for live vulnerability data. These rules are designed to be installed alongside your project's foundational steering files (`product.md`, `tech.md`, `structure.md`).

---

## Quick Start

**Choose your deployment path:**

| Audience | What you get | Where |
|----------|--------------|-------|
| **Individual developer** | Self-install globally or per project (~5 min) | Steps 0–1 below |
| **Small team** | Forked + versioned repo, onboarding one-liner, PR-gating CI (~30 min setup) | [Adoption Guide → Tier 2](docs/adoption-guide.md#3-tier-2--small-team-30-min-setup-2-min-per-dev) |
| **Enterprise / fleet** | Global steering pushed to every machine via Jamf, Intune, or Group Policy (zero per-dev effort) | [Adoption Guide → Tier 3](docs/adoption-guide.md#4-tier-3--enterprise-mdm-12-day-setup-zero-per-dev-effort) |

> **Deploying to a team or organisation?** See the [Adoption Guide](docs/adoption-guide.md) for team (shared repo), enterprise (MDM/Group Policy), CI/CD integration, and compliance overlay instructions.

The steps below cover the **individual-developer** install. For shared-repo, MDM, CI/CD, and compliance-overlay deployment, follow the [Adoption Guide](docs/adoption-guide.md).

### Step 0: Generate Foundational Steering Files (Required First)

Before installing these security rules, open Kiro IDE in your project and generate the three foundational steering files that give Kiro project-specific context:

1. Navigate to the Steering section in the Kiro panel
2. Click **Generate Steering Docs** → **Foundation steering files**
3. Review and save the generated `product.md`, `tech.md`, and `structure.md`

These files are always-loaded and teach Kiro your tech stack and architecture. The security rules in this package build on top of that foundation — without them, the rules load without codebase context. See <https://kiro.dev/docs/steering/>.

### Step 1: Install Security Rules

#### Option 1: pip install (recommended for Python teams)

```bash
pip install git+https://github.com/your-org/kiro-steering-rules.git
kiro-security-check update      # deploy rules into .kiro/
kiro-security-check validate
```

#### Option 2: npm install (recommended for Node.js teams)

```bash
npm install git+https://github.com/your-org/kiro-steering-rules.git
kiro-security-check validate
```

#### Option 3: Shell installer (any project)

```bash
git clone git@github.com:your-org/kiro-steering-rules.git
cd kiro-steering-rules
./install.sh /path/to/your/project

# Or install globally (all projects on this machine)
./install.sh --global
```

#### Option 4: Git submodule (track updates from security team)

```bash
git submodule add git@github.com:your-org/kiro-steering-rules.git .kiro-rules
.kiro-rules/install.sh .

# Later, pull updates:
git submodule update --remote .kiro-rules
.kiro-rules/install.sh .
```

---

## After Installing

Run the following to verify all security steering files are correctly installed:

```bash
kiro-security-check validate
```

Expected output confirms all four always-on rules are present with correct front-matter:

```
[PASS] secrets-management.md
[PASS] supply-chain-security.md
[PASS] authentication-standards.md
[PASS] logging-standards.md
```

Add `--json` for CI integration. This CLI check is the canonical install verification step.

---

## Security Policies

### Always-On Rules (loaded in every Kiro conversation)

Always-on files are intentionally lean (policy statements only); enforcement patterns and detailed checklists live in hooks, conditional files, and manual workflows.

| Rule | Policy | Enforcement |
|------|--------|-------------|
| `secrets-management.md` | No hardcoded secrets, credentials, API tokens, or PAT tokens in source code | Pre-write scan hook (authoritative pattern list) |
| `supply-chain-security.md` | Zero critical/high CVEs, all deps in build files, SPDX SBOM in repo root | Audit-on-change hook + CI/CD pre-push checks |
| `authentication-standards.md` | OAuth 2.0 / OIDC required, Authorization Code + PKCE, MFA for admin | Code review + architecture review |
| `logging-standards.md` | Structured JSON logs, no PII/PHI in logs (scoped to GDPR/HIPAA/CCPA), audit trail required | Log review + code review |

### Conditional Rules (activated by file type)

| Rule | Triggers On | What It Enforces |
|------|-------------|------------------|
| `package-ecosystem-security.md` | `package.json`, `requirements.txt`, `poetry.lock`, `Cargo.toml`, `go.mod`, etc. | Ecosystem-specific audit commands + SBOM generation |
| `auth-framework-patterns.md` | `*auth*`, `*login*`, `*oauth*`, `*jwt*`, `*token*`, `*session*`, `*middleware*` | Framework-specific OIDC patterns for Express, Django, Spring Boot |

`fileMatchPattern` is declared as a YAML array (e.g. `["**/*auth*", "**/*jwt*"]`), as required by Kiro for multi-pattern conditional files.

### Auto & Manual Workflows (slash commands in Kiro chat)

| Command | Inclusion | Purpose |
|---------|-----------|---------|
| `#security-audit` | manual | Full 5-phase audit: secrets, supply chain, auth, logging, dependencies |
| `#sbom-generation` | auto | Generate/validate SPDX SBOM; auto-activates on dependency/lockfile work |
| `#log-review` | auto | Audit logs for PII/PHI exposure; auto-activates on logging/PII work |

`sbom-generation` and `log-review` use `auto` inclusion — Kiro loads them when their description matches the current work, and they remain available as `#` slash commands. `security-audit` stays `manual` so the broad 5-phase audit only runs when explicitly invoked.

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

## Hooks

Hooks are the enforcement layer (they fire regardless of conversation context). Steering files declare policy intent; hooks own the authoritative enforcement patterns.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `pre-write-secret-scan.json` | `preToolUse` (write) | Scans every file write for hardcoded secrets (authoritative pattern list) |
| `dependency-audit-on-change.json` | `fileEdited` (build/lock files) | Runs the locally installed vulnerability audit tool (authoritative command list) |
| `verify-sbom-exists.json` | `fileEdited` (`sbom.spdx.json`) | Validates SBOM format when the SBOM file is modified |
| `auto-validate-rules.json` | `preToolUse` (write) | Once per session, verifies the four always-on steering files are present |

Hooks only fire on file events — never on general-purpose shell commands. Pre-push enforcement (SBOM existence, vulnerability audit, secret scan) belongs in CI/CD; see [Pre-Push CI/CD Checks](#pre-push-cicd-checks).

### Hook Prerequisites

The `dependency-audit-on-change` hook requires a locally installed audit tool for your ecosystem. No tools are downloaded at runtime (`npx` is never used — it would execute unverified remote code inside a security check).

| Ecosystem | Required tool | Install |
|-----------|--------------|---------|
| Node.js | npm (built-in) | — |
| Python | pip-audit | `pip install pip-audit` |
| Poetry | poetry | Built into poetry 1.2+ |
| Rust | cargo-audit | `cargo install cargo-audit` |
| Ruby | bundler-audit | `gem install bundler-audit` |
| Go | govulncheck | `go install golang.org/x/vuln/cmd/govulncheck@latest` |

If no audit tool is found, the hook fails loudly (exit code 1) and names the exact install command — it never silently succeeds.

---

## MCP Servers

Instead of hardcoding evolving data (CVE lists, AWS patterns) into steering files, this ruleset points Kiro at live sources of truth via [MCP](https://modelcontextprotocol.io). The config in `mcp/mcp.json` is installed to `.kiro/settings/mcp.json`.

| Server | Purpose |
|--------|---------|
| `fetch` (`mcp-fetch`) | Live web queries for OWASP Top 10, NVD CVE records, and OSV advisories |
| `aws-docs` (`awslabs.aws-documentation-mcp-server`) | AWS IAM, Secrets Manager, KMS, and security service guidance |

Ask Kiro things like *"look up CVE-2024-3094 on NVD"* or *"show me the OWASP Top 10 entry for injection"* and it will fetch current data rather than relying on a static table.

### MCP Prerequisites

MCP servers require `uv` (which provides `uvx`):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Pre-Push CI/CD Checks

Kiro hooks handle IDE-time file validation; pre-push enforcement belongs in CI/CD where it runs regardless of editor. A ready-to-use GitHub Actions template ships at `ci/pre-push-checks.yml`:

```yaml
name: Pre-Push Security Checks
on:
  push:
    branches: ['**']
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify SBOM exists
        run: test -f sbom.spdx.json || (echo "SBOM missing. Run #sbom-generation in Kiro." && exit 1)
      - name: Validate SBOM format
        run: cat sbom.spdx.json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('spdxVersion','') >= 'SPDX-2.3'"
      - name: Dependency audit (Node)
        run: test -f package.json && npm audit --audit-level=high || true
      - name: Dependency audit (Python)
        run: test -f pyproject.toml && pip-audit || true
```

---

## For Security Team Leads

### Publishing Updates

1. Make changes to steering rules, hooks, or MCP config
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
2. Add YAML frontmatter with the appropriate `inclusion` mode (keep always-on files ≤80 lines)
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

## Creating Custom Security Rules

To add a rule specific to your project, create a new `.md` file in `.kiro/steering/` using the following template. This is an **example to adapt**, not a file to copy verbatim:

```markdown
---
inclusion: always  # or: fileMatch | manual | auto
fileMatchPattern: ["**/*.py"]  # only for fileMatch inclusion; use a YAML array
# For auto inclusion, add:
# name: my-rule-name
# description: When to include this rule (used by Kiro to decide relevance)
---

# Rule Title

## Policy
[State the rule as a clear, actionable requirement. 1–3 sentences.]

## What to Do
[The action Kiro should take. Be prescriptive, not descriptive.]

## What to Avoid
[Anti-patterns to flag. Use a short table if there are multiple.]

## Compliance Mapping (optional)
- SOC 2: [relevant control]
- PCI-DSS: [relevant requirement]
- HIPAA: [relevant safeguard]
```

**Tips:**
- Keep always-on rules under 80 lines. Use manual, conditional, or auto inclusion for detailed content.
- Reference the enforcement hook if one exists: "Enforced by `hooks/my-hook.json`."
- Use file references (`#[[file:path/to/file]]`) to link live specs instead of duplicating content.

---

## Steering File Format

Every steering file follows the [everything-kiro](https://github.com/yuening8080/everything-kiro) convention:

```yaml
---
inclusion: always                       # always | fileMatch | manual | auto
fileMatchPattern: ["**/*.ts", "**/*.tsx"]  # fileMatch only; multiple patterns MUST be a YAML array
name: my-rule                           # auto only: used as the slash command
description: When Kiro should load this  # auto only: matched against the conversation
---

# Rule Content
```

Notes:
- `fileMatch` patterns are expressed as a YAML array (`["**/*.ts", "**/*.tsx"]`). A comma-separated string is **not** valid YAML for this field and silently fails to match.
- `auto` inclusion requires a `name` and `description`; Kiro decides relevance from the description and still registers the file as a `#` slash command.

This format is compatible with all steering files generated by everything-kiro's foundation generator (`product.md`, `tech.md`, `structure.md`).

---

## Project Structure

```
kiro-steering-rules/
├── steering/
│   ├── always/                  # Loaded in every Kiro conversation
│   ├── conditional/             # Loaded when matching files are opened
│   └── manual/                  # On-demand (#name) and auto-included workflows
├── overlays/                    # Compliance overlay placeholders (PCI-DSS, HIPAA, SOX, internal-tools-lite)
├── hooks/                       # Kiro agent automation hooks
├── mcp/                         # MCP server config (-> .kiro/settings/mcp.json)
├── ci/                          # CI/CD templates (pre-push security checks)
├── docs/                        # Adoption guide + examples (security-baseline.yml)
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
