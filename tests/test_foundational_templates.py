"""Validate the foundational steering templates and the --with-templates installer flag."""

import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates" / "foundational"
TEMPLATE_FILES = ["product.md", "tech.md", "structure.md"]


@pytest.mark.parametrize("name", TEMPLATE_FILES)
def test_template_exists(name):
    path = TEMPLATES_DIR / name
    assert path.is_file(), f"Missing foundational template: {name}"


@pytest.mark.parametrize("name", TEMPLATE_FILES)
def test_template_frontmatter_is_valid_yaml_always(name):
    content = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
    # Front-matter must be the very first thing in the file (no preceding blank lines).
    assert content.startswith("---"), f"{name} must start with a YAML front-matter block"
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{name} front-matter not properly closed"
    frontmatter = yaml.safe_load(parts[1])
    assert frontmatter is not None, f"{name} front-matter is empty"
    assert frontmatter.get("inclusion") == "always", (
        f"{name} must use inclusion: always, got {frontmatter.get('inclusion')!r}"
    )
    body = parts[2].strip()
    assert len(body) > 50, f"{name} has insufficient markdown body"


@pytest.mark.parametrize("name", TEMPLATE_FILES)
def test_template_has_placeholders(name):
    content = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
    assert "[PLACEHOLDER]" in content or "<!--" in content, (
        f"{name} should mark fill-in sections with [PLACEHOLDER] or <!-- INSTRUCTIONS --> blocks"
    )


def test_default_install_does_not_copy_templates():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["bash", str(REPO_ROOT / "install.sh"), tmpdir],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"install.sh failed: {result.stderr}"
        steering_dir = Path(tmpdir) / ".kiro" / "steering"
        for name in TEMPLATE_FILES:
            assert not (steering_dir / name).exists(), (
                f"default install must not copy {name} (generated files are preferred)"
            )


def test_with_templates_flag_copies_templates():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["bash", str(REPO_ROOT / "install.sh"), "--with-templates", tmpdir],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"install.sh failed: {result.stderr}"
        steering_dir = Path(tmpdir) / ".kiro" / "steering"
        for name in TEMPLATE_FILES:
            assert (steering_dir / name).exists(), f"--with-templates did not copy {name}"


def test_with_templates_flag_does_not_overwrite_existing():
    with tempfile.TemporaryDirectory() as tmpdir:
        steering_dir = Path(tmpdir) / ".kiro" / "steering"
        steering_dir.mkdir(parents=True, exist_ok=True)
        existing = steering_dir / "product.md"
        original = "# My own product overview"
        existing.write_text(original, encoding="utf-8")
        result = subprocess.run(
            ["bash", str(REPO_ROOT / "install.sh"), "--with-templates", tmpdir],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"install.sh failed: {result.stderr}"
        assert existing.read_text(encoding="utf-8") == original, (
            "--with-templates overwrote an existing product.md (must be no-clobber)"
        )
