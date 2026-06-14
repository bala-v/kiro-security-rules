"""Validate JSON validity and structure across all hook files."""

import json
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
REQUIRED_HOOK_KEYS = {"name", "version", "description", "when", "then"}
VALID_TRIGGER_TYPES = {"preToolUse", "fileEdited", "onStartup", "postTaskExecution", "userTriggered"}
VALID_ACTION_TYPES = {"askAgent", "runCommand"}


def get_all_hooks():
    return list(HOOKS_DIR.glob("*.json"))


@pytest.mark.parametrize("hook_path", get_all_hooks())
def test_hook_is_valid_json(hook_path):
    try:
        json.loads(hook_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        pytest.fail(f"{hook_path.name} is not valid JSON: {e}")


@pytest.mark.parametrize("hook_path", get_all_hooks())
def test_hook_has_required_keys(hook_path):
    data = json.loads(hook_path.read_text(encoding="utf-8"))
    missing = REQUIRED_HOOK_KEYS - set(data.keys())
    assert not missing, f"{hook_path.name} missing keys: {missing}"


@pytest.mark.parametrize("hook_path", get_all_hooks())
def test_hook_version_is_semver(hook_path):
    data = json.loads(hook_path.read_text(encoding="utf-8"))
    version = data.get("version", "")
    parts = version.split(".")
    assert len(parts) == 3, f"{hook_path.name} version '{version}' is not semver"
    assert all(p.isdigit() for p in parts), f"{hook_path.name} version '{version}' is not semver"


@pytest.mark.parametrize("hook_path", get_all_hooks())
def test_hook_trigger_type_is_valid(hook_path):
    data = json.loads(hook_path.read_text(encoding="utf-8"))
    trigger = data.get("when", {}).get("type", "")
    assert trigger in VALID_TRIGGER_TYPES, (
        f"{hook_path.name} trigger type '{trigger}' not in {VALID_TRIGGER_TYPES}"
    )


@pytest.mark.parametrize("hook_path", get_all_hooks())
def test_hook_action_type_is_valid(hook_path):
    data = json.loads(hook_path.read_text(encoding="utf-8"))
    action = data.get("then", {}).get("type", "")
    assert action in VALID_ACTION_TYPES, (
        f"{hook_path.name} action type '{action}' not in {VALID_ACTION_TYPES}"
    )


@pytest.mark.parametrize("hook_path", get_all_hooks())
def test_hook_description_not_empty(hook_path):
    data = json.loads(hook_path.read_text(encoding="utf-8"))
    desc = data.get("description", "")
    assert len(desc) > 10, f"{hook_path.name} description too short or missing"
