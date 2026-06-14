---
inclusion: always
---

# Authentication Standards

## OAuth 2.0 / OIDC Required

All applications and sub-components MUST use OAuth 2.0 with OpenID Connect (OIDC) for authentication. Custom authentication implementations are prohibited.

### Protocol Requirements

- Use **Authorization Code flow** with **PKCE** (Proof Key for Code Exchange) for all public clients
- Use **Authorization Code flow** for confidential clients with client secret or mTLS
- Validate `state` and `nonce` parameters to prevent CSRF attacks
- Use exact redirect URI matching — never allow wildcard patterns
- Validate token audience (`aud`) and issuer (`iss`) claims
- Enforce token expiration with short lifetimes (access tokens: 15 minutes max, refresh tokens: 24 hours max)
- Implement token rotation for refresh tokens

### Prohibited Patterns

- OAuth 2.0 Implicit flow
- Resource Owner Password Credentials (ROPC) flow
- Custom-built authentication systems
- Storing tokens in `localStorage` — use httpOnly secure cookies instead
- Hardcoded client secrets in public/native apps

### Token Handling

```javascript
// BAD: Storing tokens in localStorage
localStorage.setItem("access_token", token);

// GOOD: HttpOnly secure cookie
document.cookie = "session=...; HttpOnly; Secure; SameSite=Strict; Path=/";
```

### Multi-Factor Authentication

- MFA is REQUIRED for: admin access, password changes, privilege elevation, disabling MFA
- Prefer phishing-resistant MFA: WebAuthn / FIDO2 / passkeys
- Acceptable fallback: TOTP (app-based authenticators)
- Avoid SMS and email-based MFA for sensitive operations

### Session Management

- Sessions must expire after inactivity (30 minutes for standard, 15 for admin)
- Invalidate sessions on logout, password change, and privilege change
- Generate session identifiers using CSPRNG (minimum 128 bits of entropy)
- Bind sessions to client context (IP, user-agent fingerprint) for defense in depth

## Mandatory Checks

- [ ] Authentication uses OAuth 2.0 / OIDC (Authorization Code + PKCE)
- [ ] MFA enforced for admin and sensitive operations
- [ ] No custom auth implementations
- [ ] Token storage uses httpOnly secure cookies, not localStorage
- [ ] Token lifetimes are bounded (access: ≤15min, refresh: ≤24h)
- [ ] Session invalidation on logout and privilege change
