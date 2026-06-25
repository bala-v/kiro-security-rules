# Team & Enterprise Adoption Guide

This guide explains how to deploy, version, and enforce the Kiro security
steering rules across a team or an entire organisation. The individual
developer install (`git clone` + `./install.sh`) is the smallest of several
distribution paths; the highest-leverage one is **global steering pushed via
MDM/Group Policy**, which reaches every developer's machine automatically with
zero per-developer action.

> Kiro's own documentation describes this explicitly under
> [*Team steering*](https://kiro.dev/docs/steering/#team-steering): global
> steering files "can be pushed to user's PCs via MDM solutions or Group
> Policies, or downloaded by users to their PCs from a central repository, and
> placed into the `~/.kiro/steering` folder."

## Contents

1. [How Kiro steering distribution works](#1-how-kiro-steering-distribution-works)
2. [Tier 1 — Individual Developer](#2-tier-1--individual-developer-5-min)
3. [Tier 2 — Small Team](#3-tier-2--small-team-30-min-setup-2-min-per-dev)
4. [Tier 3 — Enterprise MDM](#4-tier-3--enterprise-mdm-12-day-setup-zero-per-dev-effort)
5. [Customisation & Override Model](#5-customisation--override-model)
6. [CI/CD Integration](#6-cicd-integration)
7. [4-Week Rollout Playbook](#7-4-week-rollout-playbook)
8. [Adoption Metrics](#8-adoption-metrics)

---

## 1. How Kiro steering distribution works

Kiro loads steering files from two scopes. Understanding the precedence between
them is the foundation for every deployment decision below.

| Scope | Location | Applies to | Override behaviour |
|-------|----------|------------|--------------------|
| **Global steering** | `~/.kiro/steering/` | Every workspace on the machine | Lowest precedence |
| **Workspace steering** | `<repo>/.kiro/steering/` | One project | Overrides global on conflict |

Per the Kiro docs: *"In case of conflicting instructions between global and
workspace steering, Kiro will prioritize the workspace steering instructions."*

This single fact drives the strategy:

- **Global steering is the enterprise deployment target.** Push the baseline
  ruleset to `~/.kiro/steering/` on every machine (via MDM/Group Policy) and it
  applies to all of a developer's projects with no per-repo work.
- **Workspace steering is the override channel.** A project that legitimately
  needs a relaxed rule drops a file into its own `.kiro/steering/`, which wins
  over the global baseline. See [§5](#5-customisation--override-model).

The same three components ship to both scopes (the installer copies all of
them):

```
~/.kiro/                         # (or <repo>/.kiro/ for workspace scope)
├── steering/                    # always-on + conditional + manual rules
├── hooks/                       # agent automation (e.g. pre-write secret scan)
└── settings/mcp.json            # live CVE / AWS data sources
```

### `AGENTS.md` — the cross-tool alternative

Kiro also reads [`AGENTS.md`](https://agents.md/) files from the global steering
location (`~/.kiro/steering/`) or a workspace root. `AGENTS.md` is a
vendor-neutral standard understood by several AI coding tools, so it is a good
fit for fleets that mix Kiro with other agents. The trade-off: `AGENTS.md` does
**not** support inclusion modes (`always` / `fileMatch` / `manual` / `auto`) —
it is always included in full. Use it for a small, always-on baseline; use Kiro
steering files when you need conditional or on-demand rules.

### Foundational steering files come first

The security rules build on top of Kiro's three foundational files
(`product.md`, `tech.md`, `structure.md`), which give Kiro project context. These
are **generated per project** in the Kiro IDE (Steering panel →
**Generate Steering Docs** → **Foundation steering files**) and are not shipped
by this package. Without them the security rules still load, but without
codebase context. Prompt developers to generate them once per repo as step zero.

---

## 2. Tier 1 — Individual Developer (~5 min)

A single developer self-installs the baseline globally so it applies to all of
their projects.

```bash
git clone https://github.com/your-org/kiro-security-rules.git
cd kiro-security-rules
./install.sh --global
kiro-security-check validate
```

`./install.sh --global` copies the rules to `~/.kiro/` (it never overwrites an
existing file, so local customisations survive re-runs). `validate` confirms the
four always-on rules are present with correct front-matter.

Then, **once per project**, generate the foundational steering files in the Kiro
IDE (Steering panel → **Generate Steering Docs** → **Foundation steering
files**) so the rules load with `product.md` / `tech.md` / `structure.md`
context.

---

## 3. Tier 2 — Small Team (~30 min setup, ~2 min per dev)

A team standardises on a shared, versioned copy of the ruleset.

### 3.1 Fork and pin a version

1. Fork this repo into your org (e.g. `your-org/kiro-security-rules`).
2. Tag a versioned release so every developer installs an identical, auditable
   snapshot:

   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

### 3.2 Add to the engineering onboarding runbook

Add a single line to your onboarding docs so every new hire installs the
baseline on day one:

```bash
git clone https://github.com/your-org/kiro-security-rules.git && \
  cd kiro-security-rules && ./install.sh --global && kiro-security-check validate
```

### 3.3 Gate pull requests in CI

Add a CI job that fails the build if the always-on rules are missing or have
drifted. `kiro-security-check validate` exits non-zero when a required rule is
absent, so it works directly as a gate:

```yaml
- name: Validate Kiro security rules
  run: kiro-security-check validate
```

For machine-readable output (to archive as evidence or parse in a later step),
`--json` is a top-level flag — place it before the subcommand:

```yaml
- name: Capture rules status as JSON evidence
  run: kiro-security-check --json validate > kiro-rules-status.json
```

The full org-wide gate (secret scan, dependency audit, SBOM validation) lives in
[§6](#6-cicd-integration).

### 3.4 Git submodule alternative (compliance-gated projects)

Projects that must record exactly which ruleset version was in effect at each
commit can vendor the rules as a submodule. The submodule's pinned SHA becomes a
per-commit, auditable record of the rules version:

```bash
git submodule add https://github.com/your-org/kiro-security-rules.git .kiro-rules
.kiro-rules/install.sh .

# Later, move to a newer release and record the bump in your own history:
git submodule update --remote .kiro-rules
.kiro-rules/install.sh .
git add .kiro-rules && git commit -m "Bump security rules to v1.1.0"
```

---

## 4. Tier 3 — Enterprise MDM (1–2 day setup, zero per-dev effort)

Push the baseline to `~/.kiro/steering/` on every managed machine. Developers do
nothing; the rules are simply present in every workspace. Pick the option that
matches your fleet management tooling.

All three scripts below share the same safety properties:

- **SHA256 integrity verification** of the downloaded archive **before** any file
  is extracted.
- **No-overwrite copying** (`cp -n` / `-NoClobber` / existence check) so a
  developer's local workspace customisations are never clobbered.
- A **version sentinel** written to `~/.kiro/.security-rules-version` so the
  fleet's deployed version is discoverable for reporting.
- **Read-only enforcement** (`chmod 444` / `attrib +r`) on the non-overridable
  rules — see [§5](#5-customisation--override-model).

> The Jamf (bash) and Intune (PowerShell) scripts in this guide are
> syntax-validated in CI tooling (`bash -n` and the PowerShell language parser).
> Replace `REPLACE_WITH_RELEASE_SHA256` and the artifact URLs/paths with your own
> release values before deploying.

### Option A — Jamf Pro (macOS)

Deploy as a **postinstall** script attached to a Jamf **Policy** on the
**Recurring Check-in** trigger, scoped to your developer smart group. Track the
deployed version with an **Extension Attribute** that reads
`~/.kiro/.security-rules-version` (see below).

```bash
#!/bin/bash
#
# Jamf Pro postinstall script — deploy Kiro security steering rules to global steering.
# Deploy via a Jamf Policy on the "Recurring Check-in" trigger, scoped to the
# Developer smart group. Track the deployed version with an Extension Attribute
# that reads ~/.kiro/.security-rules-version.
#
set -euo pipefail

RULES_VERSION="1.0.0"
ARCHIVE_URL="https://artifacts.example-corp.internal/kiro-security-rules/${RULES_VERSION}/kiro-security-rules.tar.gz"
EXPECTED_SHA256="REPLACE_WITH_RELEASE_SHA256"

# --- Resolve the logged-in console user (Jamf runs scripts as root) ---
loggedInUser=$(/usr/bin/stat -f%Su /dev/console)
if [ -z "$loggedInUser" ] || [ "$loggedInUser" = "root" ]; then
  echo "No console user logged in; deferring until the next check-in."
  exit 0
fi
userHome=$(/usr/bin/dscl . -read "/Users/${loggedInUser}" NFSHomeDirectory | /usr/bin/awk '{print $NF}')
kiroDir="${userHome}/.kiro"

# --- Download the release archive to a temp workspace ---
workDir=$(/usr/bin/mktemp -d)
trap 'rm -rf "$workDir"' EXIT
archivePath="${workDir}/kiro-security-rules.tar.gz"
/usr/bin/curl -fsSL "$ARCHIVE_URL" -o "$archivePath"

# --- Verify SHA256 BEFORE extracting any file ---
actualSha=$(/usr/bin/shasum -a 256 "$archivePath" | /usr/bin/awk '{print $1}')
if [ "$actualSha" != "$EXPECTED_SHA256" ]; then
  echo "SHA256 mismatch: expected ${EXPECTED_SHA256}, got ${actualSha}. Aborting."
  exit 1
fi

/usr/bin/tar -xzf "$archivePath" -C "$workDir"
rulesRoot="${workDir}/kiro-security-rules"

# --- Create the global steering directories ---
/bin/mkdir -p "${kiroDir}/steering" "${kiroDir}/hooks" "${kiroDir}/settings"

# --- Copy with -n (no-overwrite) so local developer customizations survive ---
/bin/cp -n "${rulesRoot}/steering/always/"*.md      "${kiroDir}/steering/" 2>/dev/null || true
/bin/cp -n "${rulesRoot}/steering/conditional/"*.md "${kiroDir}/steering/" 2>/dev/null || true
/bin/cp -n "${rulesRoot}/steering/manual/"*.md      "${kiroDir}/steering/" 2>/dev/null || true
/bin/cp -n "${rulesRoot}/hooks/"*.json              "${kiroDir}/hooks/"    2>/dev/null || true
/bin/cp -n "${rulesRoot}/mcp/mcp.json"              "${kiroDir}/settings/" 2>/dev/null || true

# --- Enforce non-overridable rules as read-only (defense in depth) ---
for locked in secrets-management.md authentication-standards.md; do
  [ -f "${kiroDir}/steering/${locked}" ] && /bin/chmod 444 "${kiroDir}/steering/${locked}"
done
[ -f "${kiroDir}/hooks/pre-write-secret-scan.json" ] && /bin/chmod 444 "${kiroDir}/hooks/pre-write-secret-scan.json"

# --- Write the version sentinel for fleet tracking ---
echo "$RULES_VERSION" > "${kiroDir}/.security-rules-version"

# --- Restore ownership to the user (the policy ran as root) ---
/usr/sbin/chown -R "$loggedInUser" "$kiroDir"

echo "Kiro security rules ${RULES_VERSION} deployed to ${kiroDir}"
exit 0
```

**Jamf Extension Attribute** (Settings → Computer Management → Extension
Attributes; type *Script*) to report the deployed version in inventory:

```bash
#!/bin/bash
loggedInUser=$(/usr/bin/stat -f%Su /dev/console)
sentinel="/Users/${loggedInUser}/.kiro/.security-rules-version"
if [ -f "$sentinel" ]; then
  echo "<result>$(/bin/cat "$sentinel")</result>"
else
  echo "<result>not-installed</result>"
fi
```

### Option B — Microsoft Intune (Windows/macOS)

Use the **PowerShell script** policy type on Windows or the **Shell script**
(macOS) policy type — the same script runs in the user context on both, because
`$HOME` resolves correctly on each OS. Read the sentinel with an Intune **custom
compliance** script to surface version coverage.

```powershell
#Requires -Version 5.1
<#
.SYNOPSIS
    Deploy Kiro security steering rules to per-user global steering (~/.kiro).
.DESCRIPTION
    Compatible with the Microsoft Intune "Shell script" (macOS) and
    "PowerShell script" (Windows) device-management policy types. Runs in the
    user context and writes a version sentinel for Intune custom compliance.
#>
$ErrorActionPreference = 'Stop'

$RulesVersion   = '1.0.0'
$ArchiveUrl     = "https://artifacts.example-corp.internal/kiro-security-rules/$RulesVersion/kiro-security-rules.zip"
$ExpectedSha256 = 'REPLACE_WITH_RELEASE_SHA256'

# Resolve the per-user global steering location on either OS.
$kiroDir = Join-Path $HOME '.kiro'
$workDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $workDir -Force | Out-Null

try {
    $archivePath = Join-Path $workDir 'kiro-security-rules.zip'
    Invoke-WebRequest -Uri $ArchiveUrl -OutFile $archivePath -UseBasicParsing

    # Verify SHA256 BEFORE extracting anything.
    $actualSha = (Get-FileHash -Path $archivePath -Algorithm SHA256).Hash
    if ($actualSha -ne $ExpectedSha256.ToUpper()) {
        throw "SHA256 mismatch: expected $ExpectedSha256, got $actualSha. Aborting."
    }

    Expand-Archive -Path $archivePath -DestinationPath $workDir -Force
    $rulesRoot = Join-Path $workDir 'kiro-security-rules'

    # Create the global steering directories.
    foreach ($sub in 'steering', 'hooks', 'settings') {
        New-Item -ItemType Directory -Path (Join-Path $kiroDir $sub) -Force | Out-Null
    }

    # Copy with -NoClobber so local developer customizations survive.
    $steeringDest = Join-Path $kiroDir 'steering'
    foreach ($tier in 'always', 'conditional', 'manual') {
        $src = Join-Path $rulesRoot (Join-Path 'steering' (Join-Path $tier '*.md'))
        if (Test-Path $src) {
            Copy-Item -Path $src -Destination $steeringDest -NoClobber -ErrorAction SilentlyContinue
        }
    }
    Copy-Item -Path (Join-Path $rulesRoot 'hooks/*.json') -Destination (Join-Path $kiroDir 'hooks') -NoClobber -ErrorAction SilentlyContinue
    Copy-Item -Path (Join-Path $rulesRoot 'mcp/mcp.json') -Destination (Join-Path $kiroDir 'settings') -NoClobber -ErrorAction SilentlyContinue

    # Enforce non-overridable rules as read-only (defense in depth).
    foreach ($locked in 'secrets-management.md', 'authentication-standards.md') {
        $p = Join-Path $steeringDest $locked
        if (Test-Path $p) { Set-ItemProperty -Path $p -Name IsReadOnly -Value $true }
    }

    # Write the version sentinel for fleet tracking.
    Set-Content -Path (Join-Path $kiroDir '.security-rules-version') -Value $RulesVersion -NoNewline

    Write-Output "Kiro security rules $RulesVersion deployed to $kiroDir"
}
finally {
    Remove-Item -Path $workDir -Recurse -Force -ErrorAction SilentlyContinue
}
```

### Option C — Group Policy login script (Windows AD)

No MDM required. Link this batch script under **User Configuration → Policies →
Windows Settings → Scripts → Logon** in a GPO scoped to your Developers OU. It
copies the verified archive from a UNC artifact share.

```bat
@echo off
REM ============================================================================
REM  Kiro security steering rules — Group Policy logon script (Windows AD).
REM  Link under User Configuration > Policies > Windows Settings > Scripts >
REM  Logon, in a GPO scoped to the Developers OU. No MDM required; the rules
REM  are pulled from a UNC artifact share.
REM ============================================================================
setlocal enableextensions enabledelayedexpansion

set "RULES_VERSION=1.0.0"
set "ARTIFACT_SHARE=\\fileserver.example-corp.internal\artifacts\kiro-security-rules\%RULES_VERSION%"
set "ARCHIVE=%ARTIFACT_SHARE%\kiro-security-rules.zip"
set "EXPECTED_SHA256=REPLACE_WITH_RELEASE_SHA256"
set "KIRO_DIR=%USERPROFILE%\.kiro"
set "WORK_DIR=%TEMP%\kiro-rules-%RANDOM%"

REM --- Skip if this version is already deployed ---
if exist "%KIRO_DIR%\.security-rules-version" (
    set /p INSTALLED=<"%KIRO_DIR%\.security-rules-version"
    if "!INSTALLED!"=="%RULES_VERSION%" (
        echo Kiro security rules %RULES_VERSION% already present. Skipping.
        goto :eof
    )
)

mkdir "%WORK_DIR%" 2>nul
copy /y "%ARCHIVE%" "%WORK_DIR%\kiro-security-rules.zip" >nul
if errorlevel 1 (
    echo ERROR: could not reach artifact share %ARTIFACT_SHARE%.
    goto :cleanup
)

REM --- Verify SHA256 BEFORE extracting ---
for /f "skip=1 tokens=*" %%H in ('certutil -hashfile "%WORK_DIR%\kiro-security-rules.zip" SHA256') do (
    if not defined ACTUAL_SHA set "ACTUAL_SHA=%%H"
)
set "ACTUAL_SHA=%ACTUAL_SHA: =%"
if /i not "%ACTUAL_SHA%"=="%EXPECTED_SHA256%" (
    echo ERROR: SHA256 mismatch. Expected %EXPECTED_SHA256%, got %ACTUAL_SHA%.
    goto :cleanup
)

REM --- Extract the verified archive ---
powershell -NoProfile -Command "Expand-Archive -Path '%WORK_DIR%\kiro-security-rules.zip' -DestinationPath '%WORK_DIR%' -Force"
set "RULES_ROOT=%WORK_DIR%\kiro-security-rules"

if not exist "%KIRO_DIR%\steering" mkdir "%KIRO_DIR%\steering"
if not exist "%KIRO_DIR%\hooks" mkdir "%KIRO_DIR%\hooks"
if not exist "%KIRO_DIR%\settings" mkdir "%KIRO_DIR%\settings"

REM --- Copy with no-overwrite (skip files that already exist locally) ---
for %%F in ("%RULES_ROOT%\steering\always\*.md" "%RULES_ROOT%\steering\conditional\*.md" "%RULES_ROOT%\steering\manual\*.md") do (
    if not exist "%KIRO_DIR%\steering\%%~nxF" copy "%%F" "%KIRO_DIR%\steering\" >nul
)
for %%F in ("%RULES_ROOT%\hooks\*.json") do (
    if not exist "%KIRO_DIR%\hooks\%%~nxF" copy "%%F" "%KIRO_DIR%\hooks\" >nul
)
if not exist "%KIRO_DIR%\settings\mcp.json" copy "%RULES_ROOT%\mcp\mcp.json" "%KIRO_DIR%\settings\" >nul

REM --- Enforce non-overridable rules as read-only (defense in depth) ---
if exist "%KIRO_DIR%\steering\secrets-management.md" attrib +r "%KIRO_DIR%\steering\secrets-management.md"
if exist "%KIRO_DIR%\steering\authentication-standards.md" attrib +r "%KIRO_DIR%\steering\authentication-standards.md"
if exist "%KIRO_DIR%\hooks\pre-write-secret-scan.json" attrib +r "%KIRO_DIR%\hooks\pre-write-secret-scan.json"

REM --- Write the version sentinel for fleet tracking ---
> "%KIRO_DIR%\.security-rules-version" echo %RULES_VERSION%
echo Kiro security rules %RULES_VERSION% deployed to %KIRO_DIR%.

:cleanup
if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
endlocal
goto :eof
```

### Update cadence

| Change type | Cadence | Mechanism |
|-------------|---------|-----------|
| Critical security update | Within 24 hours | MDM forced-run / immediate policy push |
| Standard improvement | Monthly | Scheduled check-in (recurring trigger) |
| Breaking change | 2-week advance notice + major version bump | Announce, then roll the new major version |

Because every script writes `~/.kiro/.security-rules-version`, you can confirm
fleet uptake of any push by reporting on that sentinel (Jamf Extension
Attribute, Intune custom compliance, or a GPO inventory script).

---

## 5. Customisation & Override Model

The override model has exactly one rule: **workspace steering beats global
steering.** Everything below follows from that.

### Workspace override pattern (worked example)

Suppose a team owns an internal support tool that must log a customer's email
address to correlate support tickets — something the global
`logging-standards.md` baseline prohibits as PII. The team overrides the rule
*only for that workspace* by creating `.kiro/steering/logging-standards.md` in
the project (workspace steering takes precedence over the global file):

```markdown
---
inclusion: always
---

# Logging Standards — Support Tool Exception

This workspace overrides the global logging baseline. Logging the customer
`email` field is permitted **in this repository only**, because it is required
to correlate support tickets and the data is already in scope for this system's
DPA. All other PII/PHI prohibitions from the global baseline remain in force:
no passwords, tokens, secrets, full card numbers, SSNs, or health data in logs.

Approved by: Security Review #1234 — expires 2026-12-31.
```

Good overrides are narrow (one field), documented (why + approval), and
time-bounded (review/expiry date).

### Compliance overlays

For projects subject to a specific regulatory regime, layer a ready-made overlay
on top of the baseline instead of editing the baseline. Placeholder overlays
ship in [`overlays/`](../overlays/):

| Overlay | Use when |
|---------|----------|
| [`pci-dss-overlay.md`](../overlays/pci-dss-overlay.md) | The project is in the Cardholder Data Environment (CDE) |
| [`hipaa-overlay.md`](../overlays/hipaa-overlay.md) | The project handles Protected Health Information (PHI) |
| [`sox-overlay.md`](../overlays/sox-overlay.md) | The project is in scope for SOX financial-reporting controls |
| [`internal-tools-lite.md`](../overlays/internal-tools-lite.md) | The project is a low-risk internal tool (no customer data, no internet exposure) |

Deploy an overlay globally (`~/.kiro/steering/`) for fleets that are uniformly
in one regime, or per project (`.kiro/steering/`) when scope varies by repo.
Each overlay uses `inclusion: always` front-matter so it loads in every
conversation for the workspace(s) it is installed into.

### Non-overridable rules

A small set of rules must never be weakened by a workspace override. Enforce
them as **read-only** (`chmod 444` on macOS/Linux, `attrib +r` on Windows) when
the MDM deploys them — all three Tier 3 scripts above do this:

- `secrets-management.md`
- `pre-write-secret-scan.json` (the authoritative secret-pattern enforcement hook)
- `authentication-standards.md`

Read-only enforcement is defence in depth: it protects the global copy from
accidental local edits. Note that a workspace file at `.kiro/steering/` would
still take precedence over a global file of the same name — so pair the
read-only global copy with the CI gate in [§6](#6-cicd-integration), which
re-checks these baselines server-side where a local workspace cannot override
them.

---

## 6. CI/CD Integration

IDE-time hooks and steering catch issues while developers work; CI enforces the
same baseline server-side, where it runs regardless of editor and cannot be
overridden by a local workspace file. A complete, reusable GitHub Actions
workflow ships at
[`docs/examples/security-baseline.yml`](examples/security-baseline.yml). Copy it
into `.github/workflows/security-baseline.yml` in each repo (or call it as a
reusable workflow).

It runs four jobs:

1. **Secret scan (Gitleaks)** over the **full git history** (`fetch-depth: 0`),
   so secrets buried in old commits are caught, not just those at the tip.

   ```yaml
   - uses: actions/checkout@v4
     with:
       fetch-depth: 0
   - uses: gitleaks/gitleaks-action@v2
     env:
       GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```

2. **Dependency audit**, conditional on which lockfiles are present — only the
   relevant ecosystems run:

   - Node — `npm audit --audit-level=high` (when `package-lock.json` exists)
   - Python — `pip-audit` (when `requirements.txt` / `poetry.lock` / `pyproject.toml` exists)
   - Rust — `cargo audit` (when `Cargo.lock` exists)

   The `if: ${{ hashFiles('**/<lockfile>') != '' }}` guard skips ecosystems a
   repo does not use.

3. **SBOM validation** — confirms an SBOM exists at `sbom.spdx.json` (or
   `sbom/*.spdx.json`) and that its `spdxVersion` is `SPDX-2.3` or newer.

4. **Kiro rules version gate (optional)** — for compliance evidence, fails the
   build unless a committed `.kiro-rules-version` sentinel matches the required
   baseline version. Remove this job if you do not pin the rules version per repo.

To additionally assert the rules are installed in the working tree, add the
Tier 2 validation step from [§3.3](#33-gate-pull-requests-in-ci)
(`kiro-security-check validate`).

---

## 7. 4-Week Rollout Playbook

A staged rollout surfaces false positives on a small group before they reach the
whole fleet.

**Week 1 — Pilot.** Install on a 3–5 person pilot group. Enable **always-on
rules only** (defer conditional/manual workflows). Collect every false positive
the rules raise during normal work.

**Weeks 2–3 — Tune.** Review the pilot's feedback. Resolve false positives by
tightening rule wording or documenting legitimate workspace overrides. Prepare
the compliance overlays ([§5](#5-customisation--override-model)) the org needs.

**Week 4 — Roll out.** Push to the full fleet via MDM ([§4](#4-tier-3--enterprise-mdm-12-day-setup-zero-per-dev-effort))
or publish the onboarding runbook one-liner ([§3.2](#32-add-to-the-engineering-onboarding-runbook)).
Turn on the CI gates ([§6](#6-cicd-integration)) in all repos. Establish a
feedback channel (e.g. a `#kiro-security-rules` chat channel) so developers can
report issues quickly.

**Ongoing.**

- **Monthly** — review override requests; high volume signals a baseline rule
  that needs tuning.
- **Quarterly** — produce a fleet audit report from the version sentinel.
- **On CVE events** — ship a hotfix on the 24-hour critical cadence
  ([§4](#4-tier-3--enterprise-mdm-12-day-setup-zero-per-dev-effort)).

---

## 8. Adoption Metrics

Track these to know whether the rollout is working and where to invest.

| Metric | Source | What it tells you |
|--------|--------|-------------------|
| **Fleet coverage %** | MDM Extension Attribute / Intune custom compliance reading `~/.kiro/.security-rules-version` | How much of the fleet actually has the current rules |
| **CI gate first-pass rate** | CI results over time | Rising = IDE-time rules are catching issues before CI, so fewer builds fail the gate |
| **Credential rotation events** | Secret-management / incident tooling | Should fall quarter-over-quarter after deployment as fewer secrets are committed |
| **Override volume** | Count of workspace override files / requests | High = too many false positives in the baseline; tune the rules |

Read these together: a high CI first-pass rate **and** falling override volume
means the baseline is well-calibrated. High override volume means the baseline
is too strict; low fleet coverage means the deployment mechanism, not the rules,
needs attention.

---

## Related documentation

- [Kiro steering documentation](https://kiro.dev/docs/steering/) — scopes,
  inclusion modes, team steering, and `AGENTS.md`.
- [Repository README](../README.md) — rule catalogue, hooks, MCP servers, and
  the CLI.
- [`overlays/`](../overlays/) — compliance overlay placeholders.
- [`docs/examples/security-baseline.yml`](examples/security-baseline.yml) — the
  full CI workflow.
