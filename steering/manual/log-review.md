---
inclusion: manual
---

# Log Review Workflow

Activate this skill with `#log-review` to audit application logs for PII/PHI exposure and compliance with structured logging standards.

## Review Process

### Phase 1: Log Format Compliance

Check all log output is structured JSON:

- [ ] Every log entry is valid JSON
- [ ] Timestamp is ISO 8601 UTC
- [ ] Level field uses standard values (DEBUG, INFO, WARN, ERROR, FATAL)
- [ ] Correlation ID present on every entry
- [ ] Action and resource fields populated

### Phase 2: PII/PHI Scan

Search for these patterns in log-generating code:

| Pattern | Risk | Look For |
|---------|------|----------|
| Email addresses | HIGH | `\S+@\S+\.\S+`, `user.email`, `getEmail()` |
| SSN / Tax IDs | CRITICAL | `\d{3}-\d{2}-\d{4}` |
| Phone numbers | HIGH | `\d{3}[-.()]\d{3}[-.]\d{4}` |
| Credit card numbers | CRITICAL | `\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}` |
| Date of birth | MEDIUM | `dob`, `birth_date`, `date_of_birth` |
| IP addresses (user) | MEDIUM | Logged without anonymization |
| Full names | MEDIUM | `user.name`, `fullName`, `customer_name` |
| Medical IDs | CRITICAL | `mrn`, `patient_id`, `health_record` |
| Logged request/response bodies | HIGH | `JSON.stringify(body)`, `req.body`, `resp.data` |

```python
# BAD: Logging PII
logger.info(f"User {user.email} requested password reset")

# GOOD: Using anonymized reference
logger.info({
    "action": "password_reset_requested",
    "user_id": user.id,
    "correlation_id": correlation_id
})
```

### Phase 3: Auth Event Logging

Verify these events are always logged:

- [ ] Login attempts (success and failure)
- [ ] Logout events
- [ ] MFA enrollment and verification
- [ ] Password changes and resets
- [ ] Token refresh
- [ ] Privilege escalation
- [ ] Account lockout
- [ ] Failed authorization attempts

### Phase 4: Sensitive Data in Logs

- [ ] No raw tokens, passwords, or secrets in any log statement
- [ ] No query strings containing tokens or secrets
- [ ] No HTTP headers containing auth info
- [ ] No stack traces containing sensitive data in production logs
- [ ] No debug logging in production

## Remediation

| Finding | Fix |
|---------|-----|
| PII in log message | Replace with anonymized identifier, add to PII blocklist |
| Missing correlation_id | Add middleware to generate and propagate correlation ID |
| Plain text log format | Convert to structured JSON logger |
| Missing audit events | Add logging at auth/data mutation points |
| Secrets in debug logs | Remove, add pre-commit hook to flag patterns |
