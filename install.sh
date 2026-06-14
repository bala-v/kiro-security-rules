#!/bin/bash
set -euo pipefail

# Kiro Security Rules — Installer
# Installs security steering rules, hooks, and templates into a Kiro project.
# Supports project-level and global installation.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GLOBAL_MODE=false
TARGET_DIR=""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

usage() {
  echo "Usage: $0 [OPTIONS] [TARGET_DIR]"
  echo ""
  echo "Options:"
  echo "  --global    Install to ~/.kiro (user-level, applies to all projects)"
  echo "  --help      Show this help"
  echo ""
  echo "Examples:"
  echo "  $0 /path/to/project     # Install into a specific project"
  echo "  $0 .                    # Install into current directory"
  echo "  $0 --global             # Install globally for all projects"
  echo ""
  echo "Components installed:"
  echo "  steering/always/      -> Always-on security policies (4 rules)"
  echo "  steering/conditional/ -> File-match triggered rules (2 rules)"
  echo "  steering/manual/      -> On-demand audit workflows (3 workflows)"
  echo "  hooks/                -> Agent security hooks (4 hooks)"
  echo "  templates/            -> Custom rule template"
}

for arg in "$@"; do
  case $arg in
    --global) GLOBAL_MODE=true ;;
    --help|-h) usage; exit 0 ;;
    *) TARGET_DIR="$arg" ;;
  esac
done

if [ "$GLOBAL_MODE" = true ]; then
  KIRO_DIR="$HOME/.kiro"
  echo -e "${BLUE}Installing globally to ${KIRO_DIR}${NC}"
elif [ -n "$TARGET_DIR" ]; then
  KIRO_DIR="$TARGET_DIR/.kiro"
  echo -e "${BLUE}Installing to ${KIRO_DIR}${NC}"
else
  echo "Error: Specify a target directory or use --global"
  echo ""
  usage
  exit 1
fi

# Create directories
mkdir -p "$KIRO_DIR/steering" "$KIRO_DIR/hooks" "$KIRO_DIR/settings"

# Copy helper
copy_if_not_exists() {
  local src="$1"
  local dest="$2"
  local filename
  filename=$(basename "$src")
  if [ -f "$dest/$filename" ]; then
    echo -e "  ${YELLOW}SKIP${NC} $filename (already exists)"
  else
    cp "$src" "$dest/"
    echo -e "  ${GREEN}COPY${NC} $filename"
  fi
}

# Install steering files
echo ""
echo -e "${GREEN}Installing steering rules...${NC}"

echo "  Always-on rules:"
for f in "$SCRIPT_DIR/steering/always/"*.md; do
  [ -f "$f" ] && copy_if_not_exists "$f" "$KIRO_DIR/steering"
done

echo "  Conditional rules (file-match):"
for f in "$SCRIPT_DIR/steering/conditional/"*.md; do
  [ -f "$f" ] && copy_if_not_exists "$f" "$KIRO_DIR/steering"
done

echo "  Manual steering (on-demand):"
for f in "$SCRIPT_DIR/steering/manual/"*.md; do
  [ -f "$f" ] && copy_if_not_exists "$f" "$KIRO_DIR/steering"
done

# Install hooks
echo ""
echo -e "${GREEN}Installing hooks...${NC}"
for f in "$SCRIPT_DIR/hooks/"*.json; do
  [ -f "$f" ] && copy_if_not_exists "$f" "$KIRO_DIR/hooks"
done

# Install template
echo ""
echo -e "${GREEN}Installing templates...${NC}"
mkdir -p "$KIRO_DIR/../templates"
for f in "$SCRIPT_DIR/templates/"*; do
  [ -f "$f" ] && copy_if_not_exists "$f" "$KIRO_DIR/../templates"
done

# Summary
echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Installed:"
echo "  $(ls "$SCRIPT_DIR/steering/always/"*.md 2>/dev/null | wc -l | tr -d ' ') always-on steering rules"
echo "  $(ls "$SCRIPT_DIR/steering/conditional/"*.md 2>/dev/null | wc -l | tr -d ' ') conditional steering rules"
echo "  $(ls "$SCRIPT_DIR/steering/manual/"*.md 2>/dev/null | wc -l | tr -d ' ') manual steering workflows"
echo "  $(ls "$SCRIPT_DIR/hooks/"*.json 2>/dev/null | wc -l | tr -d ' ') agent hooks"
echo ""
echo "To verify installation, run:"
echo "  pip install -e . && kiro-security-check validate"
echo ""
echo "To check for updates regularly, add to your CI:"
echo "  bash scripts/ci-deploy.sh --target ."
