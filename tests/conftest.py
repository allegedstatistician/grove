"""Shared fixtures.

Tests never touch ~/code/scratch. Every test gets a fresh throwaway
repository under pytest's tmp_path, so the suite is safe to run anywhere and
leaves nothing behind.
"""

import subprocess
from pathlib import Path

import pytest


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture
def scratch_repo(tmp_path: Path) -> Path:
    """A git repository with one commit on `main`. Returns the worktree root."""
    root = tmp_path / "scratch"
    root.mkdir()
    _git(["init", "-q", "-b", "main"], root)
    _git(["config", "user.email", "grove-tests@example.invalid"], root)
    _git(["config", "user.name", "grove tests"], root)
    _git(["config", "commit.gpgsign", "false"], root)
    (root / "README.md").write_text("scratch\n", encoding="utf-8")
    _git(["add", "README.md"], root)
    _git(["commit", "-qm", "initial"], root)
    return root


@pytest.fixture
def not_a_repo(tmp_path: Path) -> Path:
    """A directory that is definitely not inside a git repository."""
    plain = tmp_path / "plain"
    plain.mkdir()
    return plain
