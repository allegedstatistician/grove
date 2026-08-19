"""Checkpoints: snapshots of a working tree that do not disturb git's own state.

A checkpoint is an ordinary commit object. Taking one means:

  1. Build a tree object from the current working directory.
  2. Create a commit object pointing at that tree, parented on the previous
     checkpoint (not on HEAD â€” the checkpoint chain is its own history).
  3. Point refs/grove/checkpoints/<worktree>/<id> at that commit.

Nothing above touches HEAD, the index, or any branch. That is the whole
point: `git status` looks identical before and after.

The tree-building step (1) is the hard one and the reason this project
exists. `Repository.index` + `Index.add_all()` + `Index.write_tree()` is the
short path; walking the directory and writing blobs by hand with `hashlib`
and `zlib` is the long path. Pick one deliberately.
"""

from dataclasses import dataclass
from datetime import datetime

import pygit2


@dataclass(frozen=True, slots=True)
class Checkpoint:
    """One saved snapshot of a worktree."""

    id: int
    worktree: str
    oid: str
    message: str
    created_at: datetime

    @classmethod
    def from_commit(cls, worktree: str, checkpoint_id: int, commit: pygit2.Commit) -> "Checkpoint":
        """Build a Checkpoint from the commit object a grove ref points at."""
        raise NotImplementedError

    def to_json(self) -> str:
        """Serialise for `grove log --json`.

        `datetime` is not JSON-serialisable by default. Exercises: `json`
        default= hooks, or `dataclasses.asdict` plus a converter.
        """
        raise NotImplementedError


def save(repo: pygit2.Repository, worktree: str, message: str) -> Checkpoint:
    """Snapshot the current working tree and record it under refs/grove/.

    Raises:
        NotAGitRepository, RepositoryIsBare
    """
    raise NotImplementedError


def list_checkpoints(repo: pygit2.Repository, worktree: str) -> list[Checkpoint]:
    """Return every checkpoint for `worktree`, newest first."""
    raise NotImplementedError


def get(repo: pygit2.Repository, worktree: str, checkpoint_id: int) -> Checkpoint:
    """Look up one checkpoint.

    Raises:
        CheckpointNotFound
    """
    raise NotImplementedError


def restore(
    repo: pygit2.Repository, worktree: str, checkpoint_id: int, *, force: bool = False
) -> None:
    """Overwrite the working tree with the contents of a checkpoint.

    Destructive. Deciding what `force` guards against â€” and whether restore
    should itself take a checkpoint first â€” is a design decision.

    Raises:
        CheckpointNotFound, DirtyWorktree
    """
    raise NotImplementedError


def prune(repo: pygit2.Repository, worktree: str, keep: int) -> list[Checkpoint]:
    """Delete all but the newest `keep` checkpoints. Returns what was removed."""
    raise NotImplementedError
