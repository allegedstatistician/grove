"""The core invariant: checkpointing must be invisible to git's own state."""

import subprocess
from pathlib import Path

import pytest

from grove import checkpoint, repo
from grove.errors import CheckpointNotFound

pytestmark = pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="not implemented")


def _status(root: Path) -> str:
    out = subprocess.run(
        ["git", "status", "--porcelain=v1"], cwd=root, check=True, capture_output=True, text=True
    )
    return out.stdout


def test_save_returns_a_checkpoint_with_id_zero_first(scratch_repo: Path) -> None:
    cp = checkpoint.save(repo.open_repository(scratch_repo), "main", "first")
    assert cp.id == 0
    assert cp.message == "first"


def test_save_does_not_change_git_status(scratch_repo: Path) -> None:
    (scratch_repo / "work.txt").write_text("in progress\n", encoding="utf-8")
    before = _status(scratch_repo)
    checkpoint.save(repo.open_repository(scratch_repo), "main", "wip")
    assert _status(scratch_repo) == before


def test_save_does_not_move_head(scratch_repo: Path) -> None:
    r = repo.open_repository(scratch_repo)
    head_before = str(r.head.target)
    checkpoint.save(r, "main", "wip")
    assert str(repo.open_repository(scratch_repo).head.target) == head_before


def test_ids_increment(scratch_repo: Path) -> None:
    r = repo.open_repository(scratch_repo)
    ids = [checkpoint.save(r, "main", f"c{i}").id for i in range(3)]
    assert ids == [0, 1, 2]


def test_list_is_newest_first(scratch_repo: Path) -> None:
    r = repo.open_repository(scratch_repo)
    for i in range(3):
        checkpoint.save(r, "main", f"c{i}")
    assert [c.id for c in checkpoint.list_checkpoints(r, "main")] == [2, 1, 0]


def test_get_unknown_id_raises(scratch_repo: Path) -> None:
    with pytest.raises(CheckpointNotFound):
        checkpoint.get(repo.open_repository(scratch_repo), "main", 99)


def test_restore_brings_back_file_contents(scratch_repo: Path) -> None:
    target = scratch_repo / "work.txt"
    target.write_text("version one\n", encoding="utf-8")
    r = repo.open_repository(scratch_repo)
    cp = checkpoint.save(r, "main", "v1")
    target.write_text("version two\n", encoding="utf-8")
    checkpoint.restore(r, "main", cp.id, force=True)
    assert target.read_text(encoding="utf-8") == "version one\n"


def test_prune_keeps_the_newest(scratch_repo: Path) -> None:
    r = repo.open_repository(scratch_repo)
    for i in range(5):
        checkpoint.save(r, "main", f"c{i}")
    removed = checkpoint.prune(r, "main", keep=2)
    assert sorted(c.id for c in removed) == [0, 1, 2]
    assert [c.id for c in checkpoint.list_checkpoints(r, "main")] == [4, 3]
