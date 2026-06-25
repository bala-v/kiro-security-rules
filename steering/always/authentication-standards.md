---
inclusion: always
---

# Authentication Standards

> For live OWASP and CVE guidance, use the `fetch` MCP: ask Kiro to "show me the OWASP Top 10 entry for broken authentication."

All applications and sub-components MUST use OAuth 2.0 with OpenID Connect (OIDC). Custom authentication implementations are prohibited.

## Protocol Requirements

- Authorization Code flow with **PKCE** for public clients; client secret or mTLS for confidential clients
- Validate `state` and `nonce` to prevent CSRF
- Exact redirect URI matching — no wildcards
- Validate token audience (`aud`), issuer (`iss`), expiry, and signature
- Short token lifetimes: access tokens ≤15 min, refresh tokens ≤24 h, with refresh-token rotation

## Prohibited

- OAuth 2.0 Implicit flow and Resource Owner Password Credentials (ROPC) flow
- Custom-built authentication systems
- Storing tokens in `localStorage` — use httpOnly, Secure, SameSite cookies
- Hardcoded client secrets in public/native apps

## Multi-Factor Authentication

- Required for admin access, password changes, privilege elevation, and disabling MFA
- Prefer phishing-resistant MFA (WebAuthn / FIDO2 / passkeys); TOTP acceptable; avoid SMS/email for sensitive operations

## Session Management

- Expire sessions after inactivity (30 min standard, 15 min admin)
- Invalidate on logout, password change, and privilege change
- Generate session IDs with a CSPRNG (≥128 bits of entropy)

Framework-specific implementation patterns and the full auth anti-pattern matrix (Express/Passport, Django/FastAPI, Spring Boot) load automatically via `auth-framework-patterns.md` when you open auth-related files.
