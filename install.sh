#!/bin/bash
set -euo pipefail

# Kiro Security Rules — Installer
# Installs security steering rules, hooks, and MCP config into a Kiro project.
# Supports project-level and global installation.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GLOBAL_MODE=false
WITH_TEMPLATES=false
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
  echo "  --global          Install to ~/.kiro (user-level, applies to all projects)"
  echo "  --with-templates  Also copy foundational steering templates (product.md, tech.md,"
  echo "                    structure.md) into .kiro/steering/. Off by default — Kiro's IDE"
  echo "                    generator produces better, codebase-aware files. No-clobber copy."
  echo "  --help            Show this help"
  echo ""
  echo "Examples:"
  echo "  $0 /path/to/project              # Install into a specific project"
  echo "  $0 .                             # Install into current directory"
  echo "  $0 --global                      # Install globally for all projects"
  echo "  $0 --with-templates .            # Install + copy foundational templates"
  echo ""
  echo "Components installed:"
  echo "  steering/always/         -> Always-on security policies (4 rules)"
  echo "  steering/conditional/    -> File-match triggered rules (2 rules)"
  echo "  steering/manual/         -> On-demand & auto audit workflows (3 workflows)"
  echo "  hooks/                   -> Agent security hooks (4 hooks)"
  echo "  mcp/mcp.json             -> MCP servers for live vuln databases (.kiro/settings/)"
  echo "  templates/foundational/  -> Starter product.md/tech.md/structure.md (--with-templates)"
}

for arg in "$@"; do
  case $arg in
    --global) GLOBAL_MODE=true ;;
    --with-templates) WITH_TEMPLATES=true ;;
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

# Install MCP config (no overwrite if already exists)
echo ""
echo -e "${GREEN}Installing MCP config...${NC}"
MCP_DEST="$KIRO_DIR/settings/mcp.json"
if [ -f "$MCP_DEST" ]; then
  echo -e "  ${YELLOW}SKIP${NC} mcp.json (already exists at .kiro/settings/mcp.json)"
else
  mkdir -p "$KIRO_DIR/settings"
  cp "$SCRIPT_DIR/mcp/mcp.json" "$MCP_DEST"
  echo -e "  ${GREEN}COPY${NC} mcp.json -> .kiro/settings/mcp.json"
fi

# Optionally install foundational steering templates (opt-in via --with-templates).
# Not copied by default: Kiro's IDE generator analyses the actual codebase and
# produces better files than these fill-in-the-blank starters. The copy is
# no-clobber so an existing product.md/tech.md/structure.md is never overwritten.
if [ "$WITH_TEMPLATES" = true ]; then
  echo ""
  echo -e "${GREEN}Copying foundational steering templates...${NC}"
  for f in "$SCRIPT_DIR/templates/foundational/"*.md; do
    [ -f "$f" ] && copy_if_not_exists "$f" "$KIRO_DIR/steering"
  done
  echo -e "  ${GREEN}✓${NC} Templates copied. Open each file and replace [PLACEHOLDER] sections."
fi

# Summary
echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Installed:"
echo "  $(ls "$SCRIPT_DIR/steering/always/"*.md 2>/dev/null | wc -l | tr -d ' ') always-on steering rules"
echo "  $(ls "$SCRIPT_DIR/steering/conditional/"*.md 2>/dev/null | wc -l | tr -d ' ') conditional steering rules"
echo "  $(ls "$SCRIPT_DIR/steering/manual/"*.md 2>/dev/null | wc -l | tr -d ' ') manual/auto steering workflows"
echo "  $(ls "$SCRIPT_DIR/hooks/"*.json 2>/dev/null | wc -l | tr -d ' ') agent hooks"
echo ""
echo -e "${GREEN}VERIFY INSTALLATION (primary check):${NC}"
echo "  kiro-security-check validate"
echo ""
echo "  Expected output confirms all four always-on rules are present"
echo "  with correct front-matter. (Run 'pip install -e .' first if the"
echo "  CLI is not yet on your PATH.)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NEXT STEP — Foundational steering files"
echo ""
echo "  Security rules are now installed. Kiro also needs project-"
echo "  specific context (product.md, tech.md, structure.md) to apply"
echo "  them correctly. Without it, the rules load without codebase"
echo "  context."
echo ""
if [ "$WITH_TEMPLATES" = true ]; then
  echo "  Starter templates were copied into .kiro/steering/. Open each"
  echo "  one and replace the [PLACEHOLDER] sections with your project's"
  echo "  details, then delete any sections that don't apply."
  echo ""
  echo "  Prefer codebase-aware files? Kiro IDE -> Steering panel ->"
  echo "  'Generate Steering Docs' analyses your repo and overwrites less."
else
  echo "  RECOMMENDED: Open Kiro IDE -> Steering panel -> 'Generate"
  echo "  Steering Docs' -> 'Foundation steering files'. The generator"
  echo "  analyses your actual codebase and produces the best results."
  echo ""
  echo "  ALTERNATIVE: re-run with --with-templates to copy fill-in-the-"
  echo "  blank starter templates instead, then edit them by hand."
fi
echo ""
echo "  See: https://kiro.dev/docs/steering/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To check for updates regularly, add to your CI:"
echo "  bash scripts/ci-deploy.sh --target ."
