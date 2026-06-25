---
inclusion: always
---

# Internal Tools (Lite) Overlay

> Placeholder overlay that relaxes selected baseline rules for low-risk internal
> tooling (no customer data, no internet exposure). Drop this file into a
> project's `.kiro/steering/` to take precedence over the global baseline. It
> can only relax rules that are NOT on the non-overridable list — see
> [Adoption Guide §5](../docs/adoption-guide.md#5-customisation--override-model).

[Placeholder — document which baseline rules are relaxed and why.]

Suggested areas to cover:

- Which conditional/manual rules are out of scope for internal-only tools
- Lighter logging expectations where no PII/PHI is processed
- A required statement that secrets-management and authentication-standards
  remain in force (these are never overridable)
