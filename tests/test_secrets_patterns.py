"""Verify secret detection patterns correctly identify hardcoded secrets."""

import re
from pathlib import Path

import pytest

SECRETS_RULE = Path(__file__).resolve().parent.parent / "steering" / "always" / "secrets-management.md"

# Patterns extracted from the secrets-management.md rule
SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AKIA" + "1234567890123456"),
    (r"ghp_[0-9A-Za-z]{36}", "ghp_" + "abcdefghijklmnopqrstuvwxyz1234567890"),
    (r"gho_[0-9A-Za-z]{36}", "gho_" + "abcdefghijklmnopqrstuvwxyz1234567890"),
    (r"sk_live_[0-9a-zA-Z]{24}", "sk_live_" + "abcdefghijklmnopqrstuvwx"),
    (r"pk_live_[0-9a-zA-Z]{24}", "pk_live_" + "abcdefghijklmnopqrstuvwx"),
    (r"AIza[0-9A-Za-z\-_]{35}", "AIza" + "SyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567"),
]


@pytest.mark.parametrize("pattern, test_string", SECRET_PATTERNS)
def test_secret_pattern_matches(pattern, test_string):
    """Verify that each secret pattern matches its expected format."""
    assert re.search(pattern, test_string), f"Pattern '{pattern}' failed to match '{test_string}'"


def test_secret_patterns_do_not_false_positive():
    """Verify secret patterns don't trigger on benign strings."""
    benign = [
        "const API_URL = 'https://api.example.com'",
        "const username = 'admin'",
        "const keyName = 'primary_key'",
        "const status = 'live'",
        "function getToken() { return null; }",
    ]
    for pattern_str, _ in SECRET_PATTERNS:
        for text in benign:
            assert not re.search(pattern_str, text), (
                f"Pattern '{pattern_str}' false-positives on '{text}'"
            )


def test_rule_file_contains_secret_patterns():
    """Verify the secrets rule file itself doesn't contain real secrets."""
    content = SECRETS_RULE.read_text(encoding="utf-8")
    for pattern_str, _ in SECRET_PATTERNS:
        matches = re.findall(pattern_str, content)
        for m in matches:
            assert m == "AKIA1234567890123456" or "example" in m or "test" in m.lower(), (
                f"Possible real secret in rule file: {m}"
            )
