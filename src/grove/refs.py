"""Reading and writing grove's state, which lives entirely in git refs.

grove stores nothing outside the object database. A checkpoint is a commit
object; the pointer to it is a ref under `refs/grove/`. That means `git gc`
will not collect checkpoints, `git for-each-ref` can see them, and grove
carries no sidecar files.

Layout:
    refs/grove/checkpoints/<worktree>/<id>
"""

from collections.abc import Iterator

import pygit2

GROVE_NAMESPACE = "refs/grove"
CHECKPOINT_NAMESPACE = f"{GROVE_NAMESPACE}/checkpoints"


def checkpoint_ref_name(worktree: str, checkpoint_id: int) -> str:
    """Build the full ref name for one checkpoint.

    Note that worktree names are user input and refs have naming rules
    (see `git check-ref-format`). Sanitising is part of the job.
    """
    raise NotImplementedError


def parse_checkpoint_ref(ref_name: str) -> tuple[str, int]:
    """Inverse of `checkpoint_ref_name`: return (worktree, checkpoint_id).

    Raises:
        MalformedCheckpoint: if `ref_name` is not a grove checkpoint ref.
    """
    raise NotImplementedError


def iter_checkpoint_refs(
    repo: pygit2.Repository, worktree: str | None = None
) -> Iterator[pygit2.Reference]:
    """Yield every checkpoint ref, optionally filtered to one worktree.

    Exercises: generators, `Repository.references`, glob matching on refs.
    """
    raise NotImplementedError


def write_ref(
    repo: pygit2.Repository, name: str, oid: pygit2.Oid, *, force: bool = False
) -> pygit2.Reference:
    """Point `name` at `oid`, creating it if absent."""
    raise NotImplementedError


def delete_ref(repo: pygit2.Repository, name: str) -> None:
    """Delete a ref. No-op semantics vs. raising is your decision."""
    raise NotImplementedError


def next_checkpoint_id(repo: pygit2.Repository, worktree: str) -> int:
    """Return one past the highest existing checkpoint id for `worktree`."""
    raise NotImplementedError
