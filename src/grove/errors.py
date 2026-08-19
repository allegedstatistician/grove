"""Domain errors for grove.

Every failure grove raises on purpose is a subclass of `GroveError`, so a
caller can write `except GroveError` and catch exactly grove's failures and
nothing else. Errors raised by libraries (pygit2, subprocess) get wrapped:

    raise WorktreeNotFound(name) from err

Nothing here defines `__init__`. Deciding what each error needs to carry â€”
a path, a name, a stderr blob â€” and how it renders as a message is part of
the exercise.
"""


class GroveError(Exception):
    """Base class for every error grove raises deliberately."""


class NotAGitRepository(GroveError):
    """The path grove was pointed at is not inside a git repository."""


class RepositoryIsBare(GroveError):
    """The repository has no working tree, so worktree operations cannot apply."""


class WorktreeExists(GroveError):
    """A worktree with the requested name is already registered."""


class WorktreeNotFound(GroveError):
    """No worktree with the requested name is registered."""


class DirtyWorktree(GroveError):
    """The operation refuses to run while the worktree has uncommitted changes."""


class CheckpointNotFound(GroveError):
    """No checkpoint with the requested id exists for this worktree."""


class MalformedCheckpoint(GroveError):
    """A ref under refs/grove/ exists but does not decode into a Checkpoint."""


class GitCommandFailed(GroveError):
    """A shelled-out `git` command exited non-zero.

    Worth carrying: the argv that was run, the exit code, and stderr. Decide
    whether that belongs in attributes, in the message, or both.
    """
