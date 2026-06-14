---
inclusion: manual
---

# SBOM Generation Workflow

Activate this skill with `#sbom-generation` to generate or update the project's Software Bill of Materials in SPDX format.

## Prerequisites

- All dependencies installed and resolved
- Lock files up to date
- Working in the repository root directory

## Generation Steps

### 1. Determine Ecosystem and Run Generator

```bash
# Node.js
npx @cyclonedx/bom --output sbom.spdx.json

# Python (pip)
pip install pip-licenses
pip-licenses --format=json --output-file=sbom.spdx.json

# Python (poetry)
poetry add --group dev cyclonedx-bom
poetry run cyclonedx-py --format spdx --output sbom.spdx.json

# Rust
cargo install cargo-cyclonedx
cargo cyclonedx

# Go
go install github.com/anchore/syft@latest
syft . -o spdx-json=sbom.spdx.json

# Multi-language (general)
pip install spdx-sbom-generator
spdx-sbom-generator -p . -o sbom.spdx.json
```

### 2. Place SBOM in Repository

- **Single repository**: `sbom.spdx.json` in root
- **Monorepo**: `sbom/<component-name>.spdx.json`

### 3. Validate SBOM

```bash
# Using SPDX tools
pip install spdx-tools
spdx-validator sbom.spdx.json

# Or use the online validator
# https://tools.spdx.org/app/validate/
```

### 4. Verify SBOM Contents

- [ ] All direct dependencies listed
- [ ] All transitive dependencies listed
- [ ] Every entry has: name, version, license, supplier
- [ ] SPDX document has: creator, created timestamp, document namespace
- [ ] Format is valid SPDX 2.3+ JSON

### SBOM Update Cadence

- Every dependency change (add, update, remove)
- Every release or build
- At minimum, weekly via CI/CD pipeline

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/sbom.yml
name: SBOM Generation
on:
  push:
    paths:
      - "package.json"
      - "requirements.txt"
      - "poetry.lock"
      - "Cargo.lock"
      - "go.mod"
jobs:
  generate-sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx @cyclonedx/bom --output sbom.spdx.json
      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.spdx.json
```
