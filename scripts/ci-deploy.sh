#!/bin/bash
set -euo pipefail

# CI/CD deploy script for kiro-security-rules
# Fetches the latest security rules from the central repo and installs them
# into the current project's .kiro/ directory.
#
# Usage in team CI pipeline:
#   curl -sL https://github.com/your-org/kiro-steering-rules/releases/latest/download/bundle.sh | bash
#   bash ci-deploy.sh --target /path/to/project

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR=""
REGISTRY_URL="https://github.com/your-org/kiro-steering-rules"
VERSION="latest"

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Deploy Kiro security rules to a project."
    echo ""
    echo "Options:"
    echo "  --target DIR     Target project directory (default: current directory)"
    echo "  --version TAG    Specific version to deploy (default: latest)"
    echo "  --from-url URL   Custom registry URL"
    echo "  --help           Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --target ./my-project"
    echo "  $0 --version v1.1.0"
}

for arg in "$@"; do
    case $arg in
        --target) TARGET_DIR="$2"; shift 2 ;;
        --version) VERSION="$2"; shift 2 ;;
        --from-url) REGISTRY_URL="$2"; shift 2 ;;
        --help|-h) usage; exit 0 ;;
    esac
done

if [ -z "$TARGET_DIR" ]; then
    TARGET_DIR="."
fi

echo "=== Kiro Security Rules CI Deploy ==="
echo "Target:   $TARGET_DIR"
echo "Version:  $VERSION"
echo "Registry: $REGISTRY_URL"
echo ""

# Determine install method based on available tools
if command -v pip &>/dev/null; then
    echo "Using pip install..."
    if [ "$VERSION" = "latest" ]; then
        pip install --quiet "kiro-security-rules @ git+${REGISTRY_URL}.git"
    else
        pip install --quiet "kiro-security-rules @ git+${REGISTRY_URL}.git@${VERSION}"
    fi
    # Run the CLI to install rules into the target project
    python -m kiro_security.cli update

elif command -v npm &>/dev/null; then
    echo "Using npm install..."
    PKG_SPEC="${REGISTRY_URL}.git"
    if [ "$VERSION" != "latest" ]; then
        PKG_SPEC="${REGISTRY_URL}.git#${VERSION}"
    fi
    npm install --silent "$PKG_SPEC"
    # Run the postinstall script copies rules to .kiro/
    node -e "
        const { execSync } = require('child_process');
        execSync('node scripts/postinstall.js', { cwd: 'node_modules/kiro-security-rules' });
    "

elif [ -f "$SCRIPT_DIR/../install.sh" ]; then
    echo "Using local install.sh..."
    bash "$SCRIPT_DIR/../install.sh" "$TARGET_DIR"

else
    echo "ERROR: No package manager (pip/npm) found and no local install.sh."
    echo "Install Python or Node.js, or run install.sh directly."
    exit 1
fi

echo ""
echo "Security rules deployed successfully to $TARGET_DIR/.kiro/"
echo "Run 'kiro-security-check validate' to verify installation."
