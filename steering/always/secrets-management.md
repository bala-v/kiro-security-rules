---
inclusion: always
---

# Secrets Management

> For live CVE lookups and OWASP guidance, use the `fetch` MCP: ask Kiro to "look up CVE-YYYY-NNNNN on NVD" or "show me the OWASP Top 10 entry for sensitive data exposure."

## Policy

Never hardcode secrets. All credentials, API keys, tokens, passwords, and connection strings must come from environment variables or a secrets manager — never source code, comments, TODOs, or test fixtures. Keep `.env` files listed in `.gitignore`.

## Prohibited Patterns

Never hardcode: API keys, access tokens, refresh tokens, private keys, database connection strings with credentials, or any value matching a known provider credential format.

The pre-write secret scan hook (`hooks/pre-write-secret-scan.json`) is the authoritative enforcement point. It scans every file write against a comprehensive pattern list covering AWS, GitHub, Stripe, Google, Slack, JWT, and database connection strings. This steering file intentionally does not duplicate that list.

## Correct Approach

```python
# BAD
API_KEY = "sk_live_..."

# GOOD
import os
API_KEY = os.environ["API_KEY"]
```

## If a Secret Is Exposed

Stop work → rotate the credential immediately at its source (AWS IAM, GitHub, secrets manager) → check git history with `git log -S 'AKIA'` → run `#security-audit` Phase 1 for a full scan including git history.
