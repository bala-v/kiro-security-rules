"""Verify all 4 always-on steering files exist with correct frontmatter."""

from pathlib import Path

import pytest

ALWAYS_DIR = Path(__file__).resolve().parent.parent / "steering" / "always"
EXPECTED_RULES = [
    "secrets-management.md",
    "supply-chain-security.md",
    "authentication-standards.md",
    "logging-standards.md",
]
EXPECTED_FRONTMATTER = "inclusion: always"


@pytest.mark.parametrize("rule_name", EXPECTED_RULES)
def test_always_on_rule_exists(rule_name):
    rule_path = ALWAYS_DIR / rule_name
    assert rule_path.exists(), f"Missing always-on rule: {rule_name}"
    assert rule_path.is_file(), f"Not a file: {rule_name}"


@pytest.mark.parametrize("rule_name", EXPECTED_RULES)
def test_always_on_rule_has_correct_frontmatter(rule_name):
    content = (ALWAYS_DIR / rule_name).read_text(encoding="utf-8")
    assert EXPECTED_FRONTMATTER in content, (
        f"{rule_name} missing '{EXPECTED_FRONTMATTER}' in frontmatter"
    )


def test_no_extra_files_in_always_dir():
    actual = {f.name for f in ALWAYS_DIR.glob("*.md")}
    expected = set(EXPECTED_RULES)
    extras = actual - expected
    assert not extras, f"Unexpected files in always/ directory: {extras}"


def test_all_rules_have_yaml_frontmatter():
    for rule in EXPECTED_RULES:
        content = (ALWAYS_DIR / rule).read_text(encoding="utf-8")
        assert content.startswith("---"), f"{rule} does not start with YAML frontmatter"
        assert "---" in content[3:], f"{rule} frontmatter not closed with ---"


def test_always_on_rules_have_content():
    for rule in EXPECTED_RULES:
        content = (ALWAYS_DIR / rule).read_text(encoding="utf-8")
        body = content.split("---", 2)[-1].strip() if content.count("---") >= 2 else content
        assert len(body) > 100, f"{rule} has insufficient content (under 100 chars)"
