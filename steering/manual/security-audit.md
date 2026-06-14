---
inclusion: manual
---

# Security Audit Workflow

Activate this skill with `#security-audit` to perform a full security audit against the organization's mandatory security policies.

## Audit Process

### Phase 1: Secrets Scan
- Search entire codebase for hardcoded credential patterns (see `secrets-management.md`)
- Check `.gitignore` includes `.env`, `*.key`, `*.pem`, `secrets.*`
- Verify secrets loaded from environment variables or secrets manager
- Check git history for accidentally committed secrets

### Phase 2: Supply Chain Audit
- Run vulnerability audit per ecosystem (`npm audit`, `pip-audit`, `cargo audit`, etc.)
- Verify zero critical and zero high findings
- Confirm all dependencies declared in build files with lock files committed
- Check SBOM exists at `$REPO_ROOT/sbom.spdx.json` (or `$REPO_ROOT/sbom/` for monorepo)
- Validate SBOM is valid SPDX 2.3+ format

### Phase 3: Authentication Review
- Verify OAuth 2.0 / OIDC in use (Authorization Code + PKCE)
- Check MFA enforcement for admin routes
- Audit token handling (no localStorage, short lifetimes, rotation)
- Verify session management (timeout, invalidation, CSPRNG session IDs)

### Phase 4: Logging Review
- Confirm all log output is structured JSON
- Check no PII or PHI in log statements
- Verify correlation_id flows through all services
- Confirm audit logging for auth, authorization, and data mutations

### Phase 5: Dependency Audit
- Run dependency audit
- Check for deprecated or end-of-life dependencies
- Verify license compliance
- Confirm SBOM is up to date

## Output Format

```
[PASS/FAIL] Category — Check description
  Details: Specific findings
  Remediation: Steps to fix (if FAIL)
```

## Risk Scoring

| Severity | Criteria | Action |
|----------|----------|--------|
| CRITICAL | Hardcoded secret, no auth, PII in logs, critical CVE | Block release, fix immediately |
| HIGH | Weak auth config, missing MFA, high CVE, no SBOM | Fix within sprint |
| MEDIUM | Missing correlation_id, incomplete audit logging | Add to backlog |
| LOW | Format inconsistency, non-blocking recommendation | Track for improvement |
