"""Locating and opening the repository grove operates on.

Design note, deliberately unresolved: `grove` run from ~/code/grove will
discover *grove's own* repository, not your scratch repo. Whether the answer
is a `--repo` flag, an env var, a config file, or cwd-only-and-live-with-it
is your call. The signatures below assume an explicit start path either way.
"""

from pathlib import Path

import pygit2

from grove.errors import RepositoryIsBare, NotAGitRepository



def discover_repository(start: Path) -> Path:
    """Walk upward from `start` and return the path of the enclosing .git dir.

    Raises:
        NotAGitRepository: if no repository encloses `start`.

    Exercises: pathlib, exception chaining, `pygit2.discover_repository`.
    """
    path = pygit2.discover_repository(start)
    if path is None:
        raise NotAGitRepository(f"No repository found in {start}")
    return Path(path)


def open_repository(start: Path) -> pygit2.Repository:
    """Open the repository enclosing `start`.

    Raises:
        NotAGitRepository: if no repository encloses `start`.
        RepositoryIsBare: if the repository has no working tree.
    """
    if pygit2.discover_repository(start) is None:
        raise NotAGitRepository(f"No repository found in {start}")
    repo = pygit2.Repository(start)
    if repo.is_bare:
        raise RepositoryIsBare(f"Repository at {start} is bare")
    return repo


def repository_root(repo: pygit2.Repository) -> Path:
    """Return the working-tree root (the directory containing .git)."""
    work_directory = repo.workdir
    if work_directory is not None:
        return Path(work_directory)
    raise RepositoryIsBare("Repository has no working directory")



def is_dirty(repo: pygit2.Repository) -> bool:
    """True if the working tree or index differs from HEAD.

    Exercises: `Repository.status()`, the status-flag bitmask, and deciding
    whether untracked files count as dirty for grove's purposes.
    """

    for filepath, flags in repo.status().items():
        if flags != pygit2.enums.FileStatus.CURRENT:
            return True
    return False
