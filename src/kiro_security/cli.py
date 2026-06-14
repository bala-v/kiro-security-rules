#!/usr/bin/env python3
"""
kiro-security-check — CLI for validating Kiro security steering rules.

Usage:
    kiro-security-check validate   Check all always-on rules are present
    kiro-security-check status     Show current rule installation status
    kiro-security-check update     Pull latest rules from package registry
    kiro-security-check audit      Run full compliance audit
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .validator import find_kiro_steering_dir, print_report, run_all_checks


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate all always-on steering rules are present and correctly configured."""
    steering_dir = find_kiro_steering_dir()
    results = run_all_checks(steering_dir)
    if args.json:
        print(json.dumps(results, indent=2))
        return
    print_report(results)


def cmd_status(args: argparse.Namespace) -> None:
    """Show current installation status of security rules."""
    steering_dir = find_kiro_steering_dir()
    print(f"\nKiro Security Rules v{__version__}")
    print(f"Steering directory: {steering_dir}")
    print(f"Directory exists:   {steering_dir.exists()}")
    if steering_dir.exists():
        files = list(steering_dir.glob("*.md"))
        print(f"Steering files:     {len(files)}")
        for f in sorted(files):
            print(f"  - {f.name}")
    hooks_dir = steering_dir.parent / "hooks"
    print(f"\nHooks directory:    {hooks_dir}")
    print(f"Directory exists:   {hooks_dir.exists()}")
    if hooks_dir.exists():
        hooks = list(hooks_dir.glob("*.json"))
        print(f"Hook files:         {len(hooks)}")
        for h in sorted(hooks):
            print(f"  - {h.name}")


def cmd_update(args: argparse.Namespace) -> None:
    """Pull latest rules from the package registry."""
    print("Updating Kiro security rules...")
    steering_dir = find_kiro_steering_dir()
    pkg_root = Path(__file__).resolve().parent.parent.parent
    src_steering = pkg_root / "steering"
    src_hooks = pkg_root / "hooks"
    if not src_steering.exists():
        print("ERROR: Package source steering directory not found.")
        print("Reinstall with: pip install --force-reinstall kiro-security-rules")
        sys.exit(1)
    dest_steering = steering_dir
    dest_hooks = steering_dir.parent / "hooks"
    dest_steering.mkdir(parents=True, exist_ok=True)
    dest_hooks.mkdir(parents=True, exist_ok=True)
    count = 0
    for src_dir, dest_dir in [(src_steering, dest_steering), (src_hooks, dest_hooks)]:
        for f in src_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(src_dir)
                dest_file = dest_dir / rel
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_bytes(f.read_bytes())
                count += 1
    print(f"Updated {count} files in {dest_steering.parent}")


def cmd_audit(args: argparse.Namespace) -> None:
    """Run full compliance audit against all security policies."""
    steering_dir = find_kiro_steering_dir()
    results = run_all_checks(steering_dir)
    if args.json:
        print(json.dumps(results, indent=2))
        return
    print_report(results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kiro Security Rules — validate and manage security steering rules"
    )
    parser.add_argument("--version", action="version", version=f"kiro-security-rules v{__version__}")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate all always-on rules are present")
    subparsers.add_parser("status", help="Show current rule installation status")
    subparsers.add_parser("update", help="Pull latest rules from package registry")
    subparsers.add_parser("audit", help="Run full compliance audit")
    args = parser.parse_args()
    cmd_map = {
        "validate": cmd_validate,
        "status": cmd_status,
        "update": cmd_update,
        "audit": cmd_audit,
    }
    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
