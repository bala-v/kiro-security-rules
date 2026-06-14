"""Verify the install.sh produces the correct .kiro/ directory layout."""

import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_install_script_exists():
    install_sh = REPO_ROOT / "install.sh"
    assert install_sh.exists(), "install.sh not found"
    assert install_sh.stat().st_mode & 0o111, "install.sh is not executable"


def test_install_script_produces_correct_layout():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["bash", str(REPO_ROOT / "install.sh"), tmpdir],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"install.sh failed: {result.stderr}"
        kiro_dir = Path(tmpdir) / ".kiro"
        steering_dir = kiro_dir / "steering"
        hooks_dir = kiro_dir / "hooks"
        assert steering_dir.exists(), "steering directory not created"
        assert hooks_dir.exists(), "hooks directory not created"
        always_files = list(steering_dir.glob("*.md"))
        assert len(always_files) >= 4, (
            f"Expected at least 4 steering files, found {len(always_files)}"
        )
        hook_files = list(hooks_dir.glob("*.json"))
        assert len(hook_files) >= 3, (
            f"Expected at least 3 hook files, found {len(hook_files)}"
        )


def test_install_script_does_not_overwrite_existing():
    with tempfile.TemporaryDirectory() as tmpdir:
        kiro_dir = Path(tmpdir) / ".kiro"
        steering_dir = kiro_dir / "steering"
        steering_dir.mkdir(parents=True, exist_ok=True)
        existing_file = steering_dir / "secrets-management.md"
        original_content = "# Custom override content"
        existing_file.write_text(original_content, encoding="utf-8")
        result = subprocess.run(
            ["bash", str(REPO_ROOT / "install.sh"), tmpdir],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert existing_file.read_text(encoding="utf-8") == original_content, (
            "install.sh overwrote existing file"
        )


def test_global_install_flag():
    result = subprocess.run(
        ["bash", str(REPO_ROOT / "install.sh"), "--help"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    assert "--global" in result.stdout
