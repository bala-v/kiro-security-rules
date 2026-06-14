import json
import os
import re
import subprocess
import sys
from pathlib import Path


RULES_DIR = Path(__file__).resolve().parent.parent.parent / "steering"
ALWAYS_RULES = [
    "secrets-management.md",
    "supply-chain-security.md",
    "authentication-standards.md",
    "logging-standards.md",
]
EXPECTED_FRONTMATTER_FIELD = "inclusion: always"


def find_kiro_steering_dir() -> Path:
    """Locate the .kiro/steering/ directory by searching upward from cwd."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        kiro_dir = parent / ".kiro" / "steering"
        if kiro_dir.exists():
            return kiro_dir
    return cwd / ".kiro" / "steering"


def validate_always_on_rules(steering_dir: Path) -> list[dict]:
    """Verify all always-on steering files exist with correct frontmatter."""
    results = []
    for rule in ALWAYS_RULES:
        rule_path = steering_dir / rule
        if not rule_path.exists():
            results.append({
                "rule": rule,
                "status": "FAIL",
                "reason": f"File not found at {rule_path}",
            })
            continue
        content = rule_path.read_text(encoding="utf-8")
        if EXPECTED_FRONTMATTER_FIELD not in content:
            results.append({
                "rule": rule,
                "status": "FAIL",
                "reason": f"Missing '{EXPECTED_FRONTMATTER_FIELD}' in frontmatter",
            })
            continue
        results.append({
            "rule": rule,
            "status": "PASS",
            "reason": "",
        })
    return results


def check_secrets_in_diff() -> list[dict]:
    """Scan git diff for hardcoded secret patterns."""
    patterns = [
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
        (r"ghp_[0-9A-Za-z]{36}", "GitHub Personal Access Token"),
        (r"gho_[0-9A-Za-z]{36}", "GitHub OAuth Token"),
        (r"sk_live_[0-9a-zA-Z]{24}", "Stripe Live Secret Key"),
        (r"pk_live_[0-9a-zA-Z]{24}", "Stripe Live Publishable Key"),
        (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
        (r"xox[baprs]-[0-9A-Za-z\-]{,80}", "Slack Token"),
        (r"-----BEGIN (RSA |EC )?PRIVATE KEY-----", "Private Key"),
        (r"(password|secret|api_key|auth_token)\s*[:=]\s*['\"][^'\"]+['\"]", "Credential Assignment"),
    ]
    results = []
    try:
        diff_output = subprocess.check_output(
            ["git", "diff", "--cached", "--"], stderr=subprocess.DEVNULL, text=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [{"status": "SKIP", "reason": "Not a git repository or git not available"}]
    for line in diff_output.splitlines():
        if not line.startswith("+"):
            continue
        for pattern, label in patterns:
            if re.search(pattern, line):
                results.append({
                    "status": "FAIL",
                    "finding": f"{label} pattern detected",
                    "line": line.strip()[:120],
                })
    return results if results else [{"status": "PASS", "reason": "No secrets found in diff"}]


def check_sbom_exists() -> dict:
    """Verify SBOM in SPDX format exists in the repository root."""
    cwd = Path.cwd()
    candidates = [
        cwd / "sbom.spdx.json",
        cwd / "sbom" / "spdx.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
                if "spdxVersion" in data:
                    return {"status": "PASS", "path": str(candidate), "version": data.get("spdxVersion")}
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
    return {"status": "FAIL", "reason": "No valid SPDX SBOM found in repository root or sbom/ directory"}


def run_all_checks(steering_dir: Path | None = None) -> dict:
    """Run all validation checks and return a summary."""
    if steering_dir is None:
        steering_dir = find_kiro_steering_dir()
    return {
        "always_on_rules": validate_always_on_rules(steering_dir),
        "secrets_in_diff": check_secrets_in_diff(),
        "sbom_exists": check_sbom_exists(),
    }


def print_report(results: dict) -> None:
    """Print a human-readable validation report."""
    all_pass = True
    print("\n=== Kiro Security Rules Validation Report ===\n")

    print("--- Always-On Steering Rules ---")
    for r in results.get("always_on_rules", []):
        icon = "PASS" if r["status"] == "PASS" else "FAIL"
        print(f"  [{icon}] {r['rule']}")
        if r.get("reason"):
            print(f"        {r['reason']}")
        if r["status"] != "PASS":
            all_pass = False

    print("\n--- Secrets in Git Diff ---")
    for r in results.get("secrets_in_diff", []):
        icon = r["status"]
        print(f"  [{icon}] {r.get('reason', r.get('finding', ''))}")

    print("\n--- SBOM Validation ---")
    r = results.get("sbom_exists", {})
    icon = r.get("status", "SKIP")
    print(f"  [{icon}] {r.get('reason', r.get('path', ''))}")
    if r.get("version"):
        print(f"        Format: {r['version']}")

    print(f"\n{'All checks passed.' if all_pass else 'SOME CHECKS FAILED.'}")
    sys.exit(0 if all_pass else 1)
