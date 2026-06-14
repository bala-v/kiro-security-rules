"""Validate YAML frontmatter across all steering files."""

from pathlib import Path

import pytest
import yaml

STEERING_DIR = Path(__file__).resolve().parent.parent / "steering"


def get_all_steering_files():
    """Return all .md files across always/, conditional/, and manual/."""
    return list(STEERING_DIR.rglob("*.md"))


@pytest.mark.parametrize("file_path", get_all_steering_files())
def test_frontmatter_is_valid_yaml(file_path):
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        pytest.fail(f"{file_path.relative_to(STEERING_DIR)} missing YAML frontmatter")
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{file_path.name} frontmatter not properly closed"
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        pytest.fail(f"{file_path.name} has invalid YAML: {e}")
    assert frontmatter is not None, f"{file_path.name} frontmatter is empty"


@pytest.mark.parametrize("file_path", get_all_steering_files())
def test_frontmatter_has_valid_inclusion(file_path):
    content = file_path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    frontmatter = yaml.safe_load(parts[1])
    assert "inclusion" in frontmatter, f"{file_path.name} missing 'inclusion' field"
    assert frontmatter["inclusion"] in ("always", "fileMatch", "manual"), (
        f"{file_path.name} inclusion must be 'always', 'fileMatch', or 'manual', "
        f"got '{frontmatter['inclusion']}'"
    )


@pytest.mark.parametrize("file_path", get_all_steering_files())
def test_filematch_patterns_valid(file_path):
    content = file_path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    frontmatter = yaml.safe_load(parts[1])
    if frontmatter.get("inclusion") == "fileMatch":
        assert "fileMatchPattern" in frontmatter, (
            f"{file_path.name} has inclusion=fileMatch but no fileMatchPattern"
        )
        pattern = frontmatter["fileMatchPattern"]
        assert isinstance(pattern, str), f"{file_path.name} fileMatchPattern must be a string"


@pytest.mark.parametrize("file_path", get_all_steering_files())
def test_file_has_content_beyond_frontmatter(file_path):
    content = file_path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    body = parts[2].strip() if len(parts) >= 3 else content.strip()
    assert len(body) > 50, f"{file_path.name} has insufficient content"
