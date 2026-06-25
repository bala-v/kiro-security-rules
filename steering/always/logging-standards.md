---
inclusion: always
---

# Logging Standards

> For live compliance and logging guidance, use the `fetch` MCP: ask Kiro to "show me the OWASP logging cheat sheet."

## Structured JSON Logging

All log output MUST be structured JSON. Plain-text logs are prohibited. Every entry MUST include these fields:

`timestamp` (ISO 8601 UTC), `level`, `logger`, `message`, `correlation_id`, `user_id` (when available), `action`, `resource`, `status_code`, `duration_ms`, and `environment`.

## Audit Logging Required

Audit events MUST be logged for: authentication (login, logout, MFA, failures), authorization decisions, data mutations (create/update/delete), privilege changes, configuration changes, and other security-relevant events.

## PII/PHI in Logs

**Prohibited in all log output** (applies regardless of compliance framework):
- Raw passwords, tokens, secrets, or credentials
- Full credit card numbers (PCI-DSS applies universally)

**Prohibited under GDPR, HIPAA, and CCPA** (applies to applications handling personal data of EU residents, US health information, or California residents):
- Email addresses, phone numbers, physical addresses
- Social Security Numbers, passport numbers, national IDs
- Dates of birth
- Biometric identifiers
- Medical record numbers, diagnosis codes, treatment information
- Full names when combined with any of the above

**If your application is not subject to GDPR, HIPAA, or CCPA:**
You may override this steering file at the workspace level by creating `.kiro/steering/logging-overrides.md` with `inclusion: always`, stating which fields are permissible in your context. Workspace steering takes precedence over global steering.

## Detail

Run `#log-review` for the full PII/PHI audit workflow, the remediation table, and the audit-event checklist.
