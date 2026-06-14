---
inclusion: always
---

# Logging Standards

## Structured JSON Logging

All applications and sub-components MUST write logs in structured JSON format. Plain text logs are prohibited.

### Required Log Format

Every log entry MUST contain these fields:

```json
{
  "timestamp": "2026-06-14T10:30:00.000Z",
  "level": "INFO",
  "logger": "com.example.auth-service",
  "message": "User login succeeded",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "user_abc123",
  "action": "login",
  "resource": "/api/v1/auth/login",
  "status_code": 200,
  "duration_ms": 45,
  "source_ip": "10.0.1.42",
  "environment": "production"
}
```

### Mandatory Fields

| Field | Description | Always Required |
|-------|-------------|:---:|
| `timestamp` | ISO 8601 UTC | Yes |
| `level` | DEBUG, INFO, WARN, ERROR, FATAL | Yes |
| `logger` | Component/service name | Yes |
| `message` | Human-readable description | Yes |
| `correlation_id` | UUID tracing the entire request flow | Yes |
| `user_id` | Authenticated user or system identifier | Yes (if available) |
| `action` | The operation being performed | Yes |
| `resource` | The endpoint or resource accessed | Yes |
| `status_code` | HTTP status or application result code | Yes |
| `duration_ms` | Request processing time in milliseconds | Yes |
| `environment` | production, staging, development | Yes |

### Audit Log Requirements

Access and audit logs are REQUIRED for:
- All authentication events (login, logout, MFA enroll/verify, failures)
- All authorization decisions (grants, denials)
- All data mutations (create, update, delete)
- All privilege changes (role assignment, permission changes)
- All configuration changes
- All security-relevant events

## PII and PHI Prohibited in Logs

**NEVER** log personally identifiable information (PII) or protected health information (PHI).

### Prohibited Fields in Logs

- Email addresses
- Social Security Numbers (SSNs)
- Dates of birth
- Phone numbers
- Physical addresses
- Credit card numbers
- Medical record numbers
- Health insurance identifiers
- Biometric data
- Passport or government ID numbers
- Full names (user IDs or correlation IDs must be used instead)

### Examples

```javascript
// BAD: Logging PII
logger.info(`User ${email} logged in from IP ${ip}`);

// GOOD: Using anonymized identifiers
logger.info({ user_id: userId, source_ip: ip, action: "login" });

// BAD: Logging request body with PII
logger.error({ message: "Validation failed", body: req.body });

// GOOD: Logging only non-sensitive fields
logger.error({
  action: "validation_failed",
  field_errors: ["email", "phone"],
  correlation_id: req.correlationId
});
```

### Log Security Requirements

- Logs must never contain raw tokens, passwords, or secrets
- Log aggregation systems must enforce access controls
- Log retention must comply with data protection regulations (GDPR, CCPA, HIPAA)
- Logs must be transmitted over TLS in transit
- Log storage must be encrypted at rest

## Mandatory Pre-Commit Checks

- [ ] All log statements output structured JSON
- [ ] No PII or PHI fields in any log statement
- [ ] No secrets or tokens logged (even masked)
- [ ] Access and audit log events cover all required categories
- [ ] Correlation ID plumbing exists through the request lifecycle
