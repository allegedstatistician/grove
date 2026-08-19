"""Worktree bookkeeping via the git porcelain."""

from pathlib import Path

import pytest

from grove import worktree
from grove.errors import WorktreeNotFound

pytestmark = pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="not implemented")


def test_a_fresh_repo_has_exactly_one_worktree(scratch_repo: Path) -> None:
    assert len(worktree.list_worktrees(scratch_repo)) == 1


def test_add_registers_a_second_worktree(scratch_repo: Path) -> None:
    worktree.add(scratch_repo, "feature-x")
    names = {w.name for w in worktree.list_worktrees(scratch_repo)}
    assert "feature-x" in names


def test_added_worktree_exists_on_disk(scratch_repo: Path) -> None:
    created = worktree.add(scratch_repo, "feature-x")
    assert created.path.is_dir()
    assert (created.path / "README.md").exists()


def test_remove_deregisters(scratch_repo: Path) -> None:
    worktree.add(scratch_repo, "feature-x")
    worktree.remove(scratch_repo, "feature-x")
    assert {w.name for w in worktree.list_worktrees(scratch_repo)} == {"scratch"}


def test_remove_unknown_raises(scratch_repo: Path) -> None:
    with pytest.raises(WorktreeNotFound):
        worktree.remove(scratch_repo, "nope")


def test_porcelain_parser_handles_multiple_records() -> None:
    sample = (
        "worktree /home/d/code/scratch\n"
        "HEAD 0123456789abcdef0123456789abcdef01234567\n"
        "branch refs/heads/main\n"
        "\n"
        "worktree /home/d/code/scratch-feature\n"
        "HEAD 89abcdef0123456789abcdef0123456789abcdef\n"
        "detached\n"
    )
    parsed = worktree.parse_porcelain(sample)
    assert len(parsed) == 2
    assert parsed[0].branch == "refs/heads/main"
    assert parsed[1].is_detached is True
