"""argparse wiring for the grove CLI.

Command surface:

    grove new <name> [--branch BRANCH]   create a worktree
    grove list                           list worktrees
    grove rm <name> [--force]            remove a worktree
    grove save [-m MESSAGE]              checkpoint the current worktree
    grove log [--worktree W] [--json]    list checkpoints
    grove restore <id> [--force]         restore a checkpoint
    grove prune [--keep N]               drop old checkpoints

Every `cmd_*` returns a process exit code. `main` is the only place that
catches GroveError and turns it into a message on stderr plus a non-zero
exit â€” handlers let errors propagate.
"""

import argparse
from collections.abc import Sequence

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


def build_parser() -> argparse.ArgumentParser:
    """Construct the full parser, subparsers included.

    Exercises: `add_subparsers(dest=..., required=True)`, `set_defaults(func=...)`
    to attach handlers, and argparse's built-in --help/exit-code behaviour.
    """
    raise NotImplementedError


def cmd_new(args: argparse.Namespace) -> int:
    raise NotImplementedError


def cmd_list(args: argparse.Namespace) -> int:
    raise NotImplementedError


def cmd_rm(args: argparse.Namespace) -> int:
    raise NotImplementedError


def cmd_save(args: argparse.Namespace) -> int:
    raise NotImplementedError


def cmd_log(args: argparse.Namespace) -> int:
    raise NotImplementedError


def cmd_restore(args: argparse.Namespace) -> int:
    raise NotImplementedError


def cmd_prune(args: argparse.Namespace) -> int:
    raise NotImplementedError


def main(argv: Sequence[str] | None = None) -> int:
    """Parse argv, dispatch, translate GroveError into an exit code.

    `argv=None` means "read sys.argv" â€” that default is what makes the CLI
    testable without monkeypatching sys.argv.
    """
    raise NotImplementedError
