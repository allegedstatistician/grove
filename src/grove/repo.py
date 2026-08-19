"""Locating and opening the repository grove operates on.

Design note, deliberately unresolved: `grove` run from ~/code/grove will
discover *grove's own* repository, not your scratch repo. Whether the answer
is a `--repo` flag, an env var, a config file, or cwd-only-and-live-with-it
is your call. The signatures below assume an explicit start path either way.
"""

from pathlib import Path

import pygit2


def discover_repository(start: Path) -> Path:
    """Walk upward from `start` and return the path of the enclosing .git dir.

    Raises:
        NotAGitRepository: if no repository encloses `start`.

    Exercises: pathlib, exception chaining, `pygit2.discover_repository`.
    """
    raise NotImplementedError


def open_repository(start: Path) -> pygit2.Repository:
    """Open the repository enclosing `start`.

    Raises:
        NotAGitRepository: if no repository encloses `start`.
        RepositoryIsBare: if the repository has no working tree.
    """
    raise NotImplementedError


def repository_root(repo: pygit2.Repository) -> Path:
    """Return the working-tree root (the directory containing .git)."""
    raise NotImplementedError


def is_dirty(repo: pygit2.Repository) -> bool:
    """True if the working tree or index differs from HEAD.

    Exercises: `Repository.status()`, the status-flag bitmask, and deciding
    whether untracked files count as dirty for grove's purposes.
    """
    raise NotImplementedError
