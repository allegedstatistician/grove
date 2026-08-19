# grove

A git worktree and checkpoint manager. This is a learning project: the point
is understanding git's object model and getting fluent in Python, not
shipping a tool. See `PROJECT.md` for the spec and `CLAUDE.md` for the
contract Claude works under.

Every function body in `src/grove/` is `raise NotImplementedError`. The test
suite is the specification. Filling in the bodies is the project.

## Requirements

- Python 3.12 or newer
- git 2.30 or newer (for `worktree list --porcelain`)
- [`uv`](https://docs.astral.sh/uv/)

`pygit2` ships prebuilt wheels with libgit2 bundled for Linux x86-64 and
macOS arm64, so no system libgit2 is needed on either machine.

## Setup

Same on WSL2 and macOS.

```
uv sync
```

That creates `.venv/`, installs `pygit2`, `mypy`, and `pytest`, and installs
`grove` itself in editable mode. `.venv/` is gitignored â€” it is rebuilt per
machine and never travels through git.

Verify:

```
uv run mypy
uv run pytest
uv run grove --help
```

The first two should pass. The third should raise `NotImplementedError` â€”
that is correct, `main()` has no body yet.

You do not need to activate the venv if you prefix commands with `uv run`.
If you would rather activate it: `source .venv/bin/activate` on both
platforms, and `deactivate` to leave.

## The xfail loop

Tests for unimplemented modules carry:

```python
pytestmark = pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="not implemented")
```

While the body raises `NotImplementedError`, the test is an expected failure
and the suite is green. When you implement the function correctly, the test
passes â€” and because `strict=True`, an unexpected pass is reported as a
failure. That XPASS is the signal to delete the marker. Red means you broke
something; XPASS means you finished something.

`tests/test_errors.py` has no marker and passes today, because the error
hierarchy is the one thing already defined.

### Reading one module before coding

The scaffold intentionally omits imports that are only needed by unfinished
function bodies. Before implementing a function:

1. Read its signature and `Raises` section.
2. Search the repository for every project-specific name in the docstring.
3. Check whether the name is already defined before creating anything new.
4. Import existing names into the implementation module that uses them.
   Imports in a test module do not make those names available to source code.
5. Read the corresponding tests to identify observable behavior, including
   behavior that is documented but not yet tested.

For example, `repo.py` names `NotAGitRepository` and `RepositoryIsBare` in
docstrings. Both classes already exist in `errors.py`; Day 1 requires importing
and raising them, not defining duplicate classes.

When implementing one function at a time, add `--runxfail` to a focused pytest
command. This disables the expected-failure wrapper temporarily:

- `PASSED` means the selected behavior works.
- `FAILED` exposes the real assertion or traceback.
- `NotImplementedError` means execution reached an unfinished body.

Without `--runxfail`, unfinished tests appear as `XFAIL`, while a finished test
appears as a strict `XPASS` and makes the command exit unsuccessfully. Remove a
module's `xfail` marker only after every function covered by that marker is
implemented.

## Layout

```
src/grove/
  errors.py       every failure is a GroveError subclass
  repo.py         finding and opening the repository
  refs.py         reading and writing refs/grove/
  checkpoint.py   the object-database work â€” the heart of the project
  worktree.py     subprocess wrappers around `git worktree`
  cli.py          argparse wiring and exit codes
tests/            the specification
```

## Working on it

Two channels, same contract:

- **Claude Code**, in this repo. Reads files, runs `uv run pytest` and
  `uv run mypy`, points at line numbers. `CLAUDE.md` is loaded
  automatically.
- **A claude.ai project**, no repo access. Concepts, git internals, design
  decisions before code exists.

Neither writes function bodies. That is the arrangement.

## Scratch repository

grove operates on some *other* repository, not on itself. Create one to test
against:

```
git init ~/code/scratch
```

Running `grove` from inside `~/code/grove` will discover grove's own
repository. Resolving that â€” a `--repo` flag, an env var, or just always
`cd`-ing first â€” is an open design decision, not a bug to paper over.
