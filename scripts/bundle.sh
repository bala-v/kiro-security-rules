#!/bin/bash
set -euo pipefail

# Bundle script for kiro-security-rules
# Packages steering rules, hooks, MCP config, and CI templates into distributable artifacts.
# Output: dist/kiro-security-rules-<version>.tar.gz
#         dist/kiro-security-rules-<version>.zip

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION="${1:-$(grep 'version =' "$REPO_ROOT/pyproject.toml" | head -1 | cut -d'"' -f2)}"
OUTPUT_DIR="$REPO_ROOT/dist"
PACKAGE_NAME="kiro-security-rules"

echo "=== Kiro Security Rules Bundle ==="
echo "Version: $VERSION"
echo "Root:    $REPO_ROOT"
echo "Output:  $OUTPUT_DIR"
echo ""

mkdir -p "$OUTPUT_DIR"

# Create temporary staging directory
STAGING_DIR=$(mktemp -d)
trap "rm -rf '$STAGING_DIR'" EXIT

STAGING_PKG="$STAGING_DIR/$PACKAGE_NAME-$VERSION"
mkdir -p "$STAGING_PKG"

# Copy all distributable files
echo "Copying files..."
cp -r "$REPO_ROOT/steering" "$STAGING_PKG/steering"
cp -r "$REPO_ROOT/hooks" "$STAGING_PKG/hooks"
cp -r "$REPO_ROOT/mcp" "$STAGING_PKG/mcp"
cp -r "$REPO_ROOT/ci" "$STAGING_PKG/ci"
cp "$REPO_ROOT/install.sh" "$STAGING_PKG/"
cp "$REPO_ROOT/README.md" "$STAGING_PKG/"
cp "$REPO_ROOT/CHANGELOG.md" "$STAGING_PKG/"
cp "$REPO_ROOT/LICENSE" "$STAGING_PKG/" 2>/dev/null || true

# Create tar.gz
echo "Creating tar.gz..."
tar -czf "$OUTPUT_DIR/$PACKAGE_NAME-$VERSION.tar.gz" \
    -C "$STAGING_DIR" "$PACKAGE_NAME-$VERSION"

# Create zip
echo "Creating zip..."
(cd "$STAGING_DIR" && zip -rq "$OUTPUT_DIR/$PACKAGE_NAME-$VERSION.zip" "$PACKAGE_NAME-$VERSION")

# Generate checksums
echo "Generating checksums..."
(cd "$OUTPUT_DIR" && \
    shasum -a 256 "$PACKAGE_NAME-$VERSION.tar.gz" > "$PACKAGE_NAME-$VERSION.tar.gz.sha256" && \
    shasum -a 256 "$PACKAGE_NAME-$VERSION.zip" > "$PACKAGE_NAME-$VERSION.zip.sha256")

echo ""
echo "Done! Artifacts:"
ls -lh "$OUTPUT_DIR/$PACKAGE_NAME-$VERSION.tar.gz"
ls -lh "$OUTPUT_DIR/$PACKAGE_NAME-$VERSION.zip"
echo "SHA256:"
cat "$OUTPUT_DIR/$PACKAGE_NAME-$VERSION.tar.gz.sha256"
cat "$OUTPUT_DIR/$PACKAGE_NAME-$VERSION.zip.sha256"
