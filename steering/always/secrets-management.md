---
inclusion: always
---

# Secrets Management

## Hardcoded Secrets Prohibited

NEVER hardcode secrets, credentials, API tokens, PAT (Personal Access Tokens), passwords, connection strings, or any sensitive material in source code.

## Recognized Secret Patterns

Treat any value matching these patterns as a prohibited secret:

- AWS access keys: `AKIA`, `AGPA`, `AIDA`, `AROA`, `ASIA` prefixed strings
- GitHub tokens: `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_` prefixed strings
- Stripe keys: `sk_live_`, `pk_live_`, `sk_test_`, `pk_test_` prefixed strings
- Google API keys: `AIza` prefixed strings
- Slack tokens: `xoxb-`, `xoxp-`, `xapp-` prefixed strings
- PAT tokens and any `*_PAT` suffixed variables
- JWT tokens: three base64 segments joined by dots, starting with `eyJ`
- Private key blocks: content between `-----BEGIN` and `-----END` markers
- Database connection strings: `mongodb://user:pass@`, `postgres://user:pass@`, `mysql://user:pass@`, `jdbc:*`
- Any variable named: `password`, `secret`, `api_key`, `api_secret`, `auth_token`, `access_token`, `refresh_token`, `private_key`
- Any hardcoded string literal that looks like a randomly generated credential (high-entropy strings >20 chars near auth code)

## Correct Approach

```python
# BAD
API_KEY = "sk_live_abc123def456"

# GOOD
import os
API_KEY = os.environ["API_KEY"]
```

```javascript
// BAD
const dbPassword = "supersecret123";

// GOOD
const dbPassword = process.env.DB_PASSWORD;
```

## Mandatory Checks Before Any File Write

- [ ] No hardcoded credential patterns exist in the file
- [ ] All secrets are referenced from environment variables or a secrets manager
- [ ] `.env` files are listed in `.gitignore`
- [ ] No secrets in comments, TODOs, or test fixtures (unless using dedicated test secrets from env)

## Incident Response

If a secret is found in code:
1. STOP all work immediately
2. Remove the secret from the file
3. Rotate the credential at the source (AWS IAM, GitHub, secret manager, etc.)
4. Check git history — if committed, treat as compromised and rotate
5. Scan the repository for similar exposures
