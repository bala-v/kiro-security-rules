---
inclusion: fileMatch
fileMatchPattern: ["**/*auth*", "**/*login*", "**/*oauth*", "**/*oidc*", "**/*sso*", "**/*jwt*", "**/*token*", "**/*session*", "**/*middleware*"]
---

# Auth Framework Patterns

This rule activates when authentication-related files are opened. Apply the framework-specific patterns below.

## Express.js / Node.js (Passport.js)

```javascript
// CORRECT: OAuth 2.0 with PKCE via Passport
const passport = require("passport");
const OIDCStrategy = require("openid-client").Strategy;

passport.use(
  "oidc",
  new OIDCStrategy(
    {
      issuer: process.env.OIDC_ISSUER,
      clientID: process.env.OIDC_CLIENT_ID,
      clientSecret: process.env.OIDC_CLIENT_SECRET,
      redirectUri: process.env.OIDC_REDIRECT_URI,
    },
    (tokens, user, done) => {
      return done(null, { id: user.sub, email: user.email });
    }
  )
);

// WRONG: Custom JWT verification without OIDC
// WRONG: Storing tokens in localStorage on the client
```

## Python (Django / FastAPI)

```python
# CORRECT: Django with OIDC
from mozilla_django_oidc import auth

OIDC_RP_CLIENT_ID = os.environ["OIDC_CLIENT_ID"]
OIDC_RP_CLIENT_SECRET = os.environ["OIDC_CLIENT_SECRET"]

# CORRECT: FastAPI with OIDC
from fastapi import Depends, HTTPException
from fastapi.security import OpenIdConnect

oauth2_scheme = OpenIdConnect(
    openIdConnectUrl=f"{os.environ['OIDC_ISSUER']}/.well-known/openid-configuration"
)
```

## Spring Boot / Java

```java
// CORRECT: Spring Security with OIDC
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .oauth2Login(withDefaults())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(withDefaults()));
        return http.build();
    }
}
```

## Common Auth Anti-Patterns to Flag

| Anti-Pattern | Severity | Fix |
|-------------|----------|-----|
| Custom password hashing | CRITICAL | Use OIDC provider |
| JWT without OIDC discovery | HIGH | Use OIDC with JWKS endpoint |
| Token in localStorage | HIGH | Use httpOnly secure cookies |
| Missing PKCE in public client | HIGH | Add PKCE challenge |
| No state parameter validation | HIGH | Validate state on callback |
| `localStorage` for session data | MEDIUM | Use session cookies |
| Hardcoded OIDC client secret | CRITICAL | Use env variables |
| No MFA enforcement for admin | HIGH | Enforce MFA check middleware |
| Session never invalidated | HIGH | Add session revocation on logout |

## Auth Middleware Checklist

- [ ] OAuth 2.0 / OIDC flow with Authorization Code + PKCE
- [ ] Token validation: audience, issuer, expiry, signature
- [ ] MFA check for admin/privileged routes
- [ ] Session binding (httpOnly, Secure, SameSite cookies)
- [ ] CSRF protection on auth endpoints
- [ ] Rate limiting on login, MFA, password reset endpoints
- [ ] Uniform error responses (no user enumeration)
- [ ] Logging of auth events (login, logout, failures) with correlation_id
