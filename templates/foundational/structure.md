---
inclusion: always
---

# Project Structure

<!--
  INSTRUCTIONS: Describe how this codebase is organised so Kiro generates files in the right
  places with the right naming. Be prescriptive. Remove sections that don't apply.
  Aim for <80 lines. The directory tree and naming sections have the highest impact.
-->

## Directory Layout

<!-- Paste your actual top-level directory tree here. Keep it to 2–3 levels deep. -->
```
[YOUR_PROJECT_ROOT]/
  src/
    [module or feature directories here]
  tests/
    unit/
    integration/
    e2e/
  docs/
  scripts/
  .kiro/
    steering/
    hooks/
    settings/
```

## Naming Conventions

### Files & Directories
- **Source files:** [e.g. kebab-case: `user-profile.ts` / snake_case: `user_profile.py`]
- **Test files:** [e.g. `*.test.ts` co-located with source / `test_*.py` in `tests/`]
- **Components:** [e.g. PascalCase: `UserProfile.tsx`]
- **Directories:** [e.g. kebab-case always]

### Code Identifiers
- **Functions / methods:** [e.g. camelCase / snake_case]
- **Classes / interfaces / types:** [e.g. PascalCase always]
- **Constants:** [e.g. SCREAMING_SNAKE_CASE for module-level / camelCase for local]
- **Booleans:** [e.g. prefix with `is`, `has`, `can`: `isLoading`, `hasPermission`]
- **Event handlers:** [e.g. prefix with `handle`: `handleSubmit`, `handleUserClick`]

## Module & Import Patterns

### Import Order
[e.g. "1. Node built-ins  2. External packages  3. Internal packages (@org/*)  4. Relative imports"]

### Path Aliases
- `@/` → `src/`
- [Add others or remove section if no aliases are configured]

### Barrel Files
[e.g. "Each module has an index.ts that re-exports its public API. Import from the index."]
[e.g. "No barrel files — import directly from source. Barrel files cause circular deps here."]

## Architectural Patterns

### Layering
[e.g. "Three-layer: routes → services → repositories. Routes never access the DB directly."]
[e.g. "Feature-slice: each feature owns its routes, services, and data access. No cross-feature imports."]

### Error Handling
[e.g. "All errors are typed. No raw throws across module boundaries."]
[e.g. "Service layer throws domain errors. Route layer catches and maps to HTTP status codes."]

### Testing Placement
[e.g. "Unit tests co-located with source: `user-service.ts` → `user-service.test.ts`"]
[e.g. "Integration tests in `tests/integration/`, named after the module they test."]

## What Not To Do

- [e.g. "Do not add business logic to route handlers — it belongs in the service layer"]
- [e.g. "Do not use default exports — named exports only"]
- [e.g. "Do not add new env vars without updating .env.example and deployment docs"]
- [e.g. "Do not commit directly to main — all changes go through PRs"]
