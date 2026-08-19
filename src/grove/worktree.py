"""Worktree add/remove/list, by shelling out to `git worktree`.

libgit2's worktree API exists, but the porcelain does bookkeeping (gitdir
files, admin entries under .git/worktrees/) that is fiddly to reproduce and
not what this project is trying to teach. So: subprocess for these three
operations only, and pygit2 for everything touching the object database.

Never pass `shell=True`. Build argv as a list.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Worktree:
    """One registered worktree, as reported by `git worktree list --porcelain`."""

    name: str
    path: Path
    branch: str | None
    head: str
    is_bare: bool
    is_detached: bool


def run_git(args: Sequence[str], cwd: Path) -> str:
    """Run a git subcommand and return stdout.

    Raises:
        GitCommandFailed: on non-zero exit, carrying argv/code/stderr.

    Exercises: `subprocess.run`, capture_output, text mode, and why
    check=True's CalledProcessError should be wrapped rather than surfaced.
    """
    raise NotImplementedError


def parse_porcelain(output: str) -> list[Worktree]: 
    """Parse `git worktree list --porcelain` into Worktree records.

    The format is line-oriented, records separated by blank lines. Exercises:
    string splitting, generators, and resisting the urge to reach for regex.
    """
    raise NotImplementedError


def list_worktrees(repo_root: Path) -> list[Worktree]:
    """Every worktree registered against this repository, main one included."""
    raise NotImplementedError


def add(repo_root: Path, name: str, branch: str | None = None) -> Worktree:
    """Create a worktree at a path derived from `name`.

    Where worktrees get placed relative to the repo is a layout decision:
    siblings of the repo, a `.worktrees/` subdirectory, or a configured root.

    Raises:
        WorktreeExists, GitCommandFailed
    """
    raise NotImplementedError


def remove(repo_root: Path, name: str, *, force: bool = False) -> None:
    """Remove a worktree and its admin entry.

    Raises:
        WorktreeNotFound, DirtyWorktree, GitCommandFailed
    """
    raise NotImplementedError


def current_worktree_name(cwd: Path) -> str:
    """Which worktree is `cwd` inside? Used to default the --worktree flag."""
    raise NotImplementedError
