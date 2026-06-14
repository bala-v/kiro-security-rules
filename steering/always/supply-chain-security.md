---
inclusion: always
---

# Supply Chain Security

## Zero Critical and Zero High Vulnerabilities

The project MUST have zero critical and zero high severity known vulnerabilities across all direct and transitive dependencies.

Before adding or updating any dependency:
1. Check vulnerability status: `npm audit`, `pip audit`, `poetry audit`, `cargo audit`, etc.
2. If the dependency introduces critical or high CVEs, DO NOT proceed — find an alternative or file a security exception
3. Run full audit after every dependency change

## All Dependencies Declared in Build Files

Every direct and transitive dependency MUST be explicitly declared in the project's build/package manifest:

| Ecosystem | Build File |
|-----------|-----------|
| Node.js | `package.json` + `package-lock.json` or `yarn.lock` |
| Python | `pyproject.toml` or `requirements.txt` + `poetry.lock` |
| Rust | `Cargo.toml` + `Cargo.lock` |
| Go | `go.mod` + `go.sum` |
| Ruby | `Gemfile` + `Gemfile.lock` |
| Java | `pom.xml` or `build.gradle` + lock file |

- Lock files MUST be committed to version control
- NEVER install dependencies without persisting to the build file
- Removing a dependency must also remove it from the build file

## SBOM Generation in SPDX Format

A full detailed Software Bill of Materials MUST be generated in **SPDX 2.3+ format** and stored in the repository.

### Location

- **Single repository**: `$REPO_ROOT/sbom.spdx.json`
- **Monorepo**: `$REPO_ROOT/sbom/<component-name>.spdx.json`

### Generation Commands

```bash
# Node.js
npx @cyclonedx/bom --output sbom.spdx.json

# Python (pip)
pip-licenses --format=json --output-file=sbom.spdx.json

# Python (poetry)
poetry run cyclonedx-py --format spdx --output sbom.spdx.json

# General
pip install spdx-sbom-generator
spdx-sbom-generator -p . -o sbom.spdx.json
```

### SBOM Requirements

- [ ] Generated in SPDX 2.3+ format
- [ ] Covers all direct and transitive dependencies
- [ ] Includes version numbers for every package
- [ ] Includes license information for every package
- [ ] Updated whenever dependencies change
- [ ] Validated with `spdx-validator` or equivalent tool

## Mandatory Pre-Commit Checks

- [ ] `npm audit` / `pip audit` / equivalent passes with zero critical and zero high findings
- [ ] All dependencies declared in build files
- [ ] Lock files up to date and committed
- [ ] SBOM exists at the required path and is valid SPDX
