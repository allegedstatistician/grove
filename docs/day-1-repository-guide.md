# Day 1 guide: repository discovery and state

This guide expands the Day 1 work in [`src/grove/repo.py`](../src/grove/repo.py).
It explains the behavior to implement without supplying Grove's function
bodies. The six existing tests in [`tests/test_repo.py`](../tests/test_repo.py)
remain the executable specification.

## Outcome

At the end of Day 1, Grove should be able to:

1. Start from a directory inside a normal Git working tree and locate its Git
   directory.
2. Translate "this path is not in a repository" into Grove's
   `NotAGitRepository` domain error.
3. Open the discovered repository with pygit2.
4. Reject bare repositories with `RepositoryIsBare`.
5. Return the working-tree root, not the Git metadata directory.
6. Tell whether tracked, staged, deleted, or untracked working-tree content is
   dirty.

The dependency flow is:

```text
discover_repository(start)
        |
        v
open_repository(start) -----> reject a bare repository
        |
        +-----> repository_root(repo)
        |
        +-----> is_dirty(repo)
```

Implement and understand the functions in that order.

## Before coding: resolve names and imports

The scaffold omits imports that are only needed inside unfinished function
bodies. A name in a docstring describes part of the contract, but it does not
automatically exist in that module's namespace.

For Day 1, both domain errors already exist:

- `NotAGitRepository` is defined in `src/grove/errors.py`.
- `RepositoryIsBare` is defined in `src/grove/errors.py`.

Import those existing classes into `repo.py` and raise them at the appropriate
boundaries. Do **not** define either class again. The import of
`NotAGitRepository` in `tests/test_repo.py` belongs only to the test module;
it does not make the name available inside `grove.repo`.

Use this pre-implementation scan for every later module:

1. Read the function signature and `Raises` section.
2. Search the repository for each Grove-specific name.
3. Decide whether the name already exists and needs an import, or is genuinely
   yours to define.
4. Read the tests that exercise the function.
5. Note promises in the docstring that currently lack a test.

## Reading focused pytest results

The module-level `xfail` marker expects `NotImplementedError`. That makes the
normal output counterintuitive during one-function-at-a-time work:

| Result | Meaning while the marker exists |
|---|---|
| `XFAIL (not implemented)` | The test reached an unfinished body. Its assertions did not pass. |
| strict `XPASS` | The test no longer raised `NotImplementedError`; this is progress, but strict mode makes the command exit nonzero. |
| `FAILED` | A different exception or assertion failure occurred. Read the innermost frame in Grove source. |

Pytest may place `[XPASS(strict)] not implemented` under a `FAILURES` heading.
That wording still means the test body completed successfully; the failure is
the strict marker objecting that an expected failure unexpectedly passed. It is
not an assertion failure in the implementation.

For a clear red/green loop, temporarily disable the wrapper for the selected
tests:

```sh
uv run pytest tests/test_repo.py -k discover --runxfail -v
```

With `--runxfail`, `PASSED` means the implementation satisfied the assertion,
and `FAILED` shows the underlying traceback. Remove the module-level marker
only after all six repository tests can pass together.

## The two paths you must keep separate

A normal repository has at least two relevant locations:

```text
/project/               working-tree root (`repo.workdir`)
/project/.git/          Git metadata directory (`repo.path`)
```

The working tree contains files a person edits. The Git directory contains
objects, refs, the index, configuration, and other administrative data.

For the ordinary repository created by the test fixture:

- `discover_repository(...)` should return a `Path` ending in `.git`.
- `repository_root(...)` should return the parent working directory.
- Do not derive the working-tree root by blindly taking `repo.path.parent`.
  That assumption becomes unreliable for linked worktrees, whose Git
  administrative directory is elsewhere. pygit2 already exposes the correct
  answer as `repo.workdir`.

Relevant documentation:

- [pygit2 repository API](https://www.pygit2.org/repository.html)
- [Git repository layout](https://git-scm.com/docs/gitrepository-layout)
- [Git worktree details](https://git-scm.com/docs/git-worktree)

## Task 1: `discover_repository`

Location: [`src/grove/repo.py`](../src/grove/repo.py#L14)

### Contract

Given a `pathlib.Path`, search that path and its parents for a repository. On
success, return the Git directory as a `Path`. If no repository is found,
raise `NotAGitRepository` and include the starting path in the error message.

### Required existing name

Import `NotAGitRepository` from `grove.errors`. It is part of the initial
scaffold; do not create another class with the same name.

The existing tests require discovery from:

- the repository root itself; and
- a nested directory such as `scratch/a/b`.

They also require a directory outside every repository to raise the named
Grove error.

### Library API

Use [`pygit2.discover_repository`](https://www.pygit2.org/repository.html#pygit2.discover_repository).
Its important behavior is easy to miss: failure is represented by `None`, not
by an exception. Its installed type is effectively:

```python
def discover_repository(path: str | Path, ...) -> str | None: ...
```

A small, generic example of narrowing that result is:

```python
found = pygit2.discover_repository(candidate)
if found is None:
    raise LookupError(candidate)
```

Do not copy the example's `LookupError` into Grove. Grove already has the
more precise `NotAGitRepository` type.

### Python concepts exercised

- **`Optional` narrowing:** after an explicit `is None` check, mypy knows the
  result is a `str` rather than `str | None`.
- **Boundary conversion:** pygit2 returns a string; Grove's public interface
  returns `Path`.
- **Domain errors:** a library's missing-value convention is translated into
  an error meaningful to Grove's callers.

### Decisions and edge cases

- Keep the default `across_fs=False`. Grove does not need to cross filesystem
  boundaries during discovery.
- The current contract treats `start` as a directory. Do not expand the task
  to invent behavior for nonexistent paths unless a new test and documented
  reason require it.
- A returned path may contain a trailing separator. Constructing a `Path`
  handles that without manual string trimming.
- There is no underlying exception to chain when discovery simply returns
  `None`. Exception chaining applies only when translating a real caught
  exception.

### Completion check

These three tests should reach XPASS while the module marker remains:

```sh
uv run pytest tests/test_repo.py::test_discover_finds_the_enclosing_repository tests/test_repo.py::test_discover_walks_up_from_a_subdirectory tests/test_repo.py::test_discover_raises_outside_a_repository -v
```

An XPASS is expected at this stage; do not remove the module-level marker
until all Day 1 functions are complete.

## Task 2: `open_repository`

Location: [`src/grove/repo.py`](../src/grove/repo.py#L25)

### Contract

Open the repository enclosing `start` and return a `pygit2.Repository`.
Preserve the domain behavior established by Task 1:

- outside a repository -> `NotAGitRepository`;
- repository has no working tree -> `RepositoryIsBare`.

Both error classes already exist in `grove.errors` and must be imported into
`repo.py`. Reuse `discover_repository` so this function does not duplicate the
`None` check or `NotAGitRepository` construction.

The first rule suggests reusing `discover_repository` instead of duplicating
its discovery and error translation.

### Library API

Construct a [`pygit2.Repository`](https://www.pygit2.org/repository.html#pygit2.Repository)
from the discovered Git-directory path:

```python
git_dir = pygit2.discover_repository(candidate)
opened = pygit2.Repository(git_dir)
```

That example omits the required `None` narrowing and Grove error handling; it
only demonstrates the library objects involved.

Use the repository's `is_bare` boolean property to identify a bare
repository. Do not guess from path names: a bare repository does not have to
end in `.git`.

### Python concepts exercised

- **Function composition:** build the higher-level operation from the
  already-tested discovery operation.
- **Early validation:** reject an object that cannot satisfy Grove's
  worktree-oriented contract before returning it.
- **Exception translation and chaining:** if you catch a specific pygit2
  exception and translate it, use `raise GroveError(...) from err` so the
  original cause remains visible. See [Python's exception-chaining
  documentation](https://docs.python.org/3.12/tutorial/errors.html#exception-chaining).

Do not catch `Exception`. Only catch a library exception if you can name the
failure it represents and translate it into an existing, accurate Grove
error. Unexpected programming and operating-system errors should remain
visible.

### Suggested missing test

The docstring promises bare-repository rejection, but the current test file
does not verify it. After the existing Day 1 tests pass, add a test that:

1. creates a temporary bare repository;
2. calls `open_repository` with it; and
3. asserts `RepositoryIsBare`.

Use the existing `tmp_path` fixture and the fixture's `_git` style rather
than a real repository outside pytest's temporary directory.

## Task 3: `repository_root`

Location: [`src/grove/repo.py`](../src/grove/repo.py#L35)

### Contract

Return the directory containing the checked-out files. For the scratch
fixture, that is the `scratch_repo` path, not `scratch_repo / ".git"`.

### Library API

Read [`Repository.workdir`](https://www.pygit2.org/repository.html#pygit2.Repository.workdir).
The property is typed as `str | None`: normal repositories have a normalized
working-directory path, while bare repositories return `None`.

### Installed typing mismatch

pygit2 1.20 contains conflicting type information. Its lower-level stub and
runtime documentation describe `workdir` as `str | None`, but the public
`BaseRepository` class annotates it as `str`. Some editors therefore warn that
`workdir is not None` is always true, even though bare repositories return
`None` at runtime.

Use the separately typed `repo.is_bare` boolean to validate the domain case
before reading `workdir`. This expresses Grove's actual rule and avoids
`# type: ignore` or `cast()` workarounds for a third-party annotation mismatch.

A generic nullable-property example is:

```python
value = object_with_optional_path.workdir
if value is None:
    raise RuntimeError("no working directory")
```

Again, Grove should use its existing `RepositoryIsBare` domain error rather
than the generic exception in the example.

### Python concepts exercised

- **`Optional` narrowing:** mypy requires proof that `workdir` is not `None`
  before it can safely become a `Path`.
- **Defensive API design:** even though `open_repository` rejects bare repos,
  callers can pass any `pygit2.Repository` directly to this function. The
  helper should keep its own promise.
- **Representation conversion:** expose filesystem locations as `Path`
  objects consistently inside Grove.

Do not use an `assert` to narrow `workdir`. A bare repository is a possible
runtime input, not an impossible programmer state, so it deserves a domain
error that remains active under optimized Python execution.

### Completion check

```sh
uv run pytest tests/test_repo.py::test_repository_root_is_the_worktree_not_the_git_dir -v
```

## Task 4: `is_dirty`

Location: [`src/grove/repo.py`](../src/grove/repo.py#L40)

### Mental model: three states, two comparisons

Git status is not merely "different from the last commit." It compares:

```text
HEAD tree  <---- INDEX_* flags ---->  index
index      <------ WT_* flags ------> working tree
```

Examples:

| Situation | Meaning | Representative flag family |
|---|---|---|
| `git add` staged a new file | index differs from HEAD | `INDEX_NEW` |
| tracked file edited but not staged | worktree differs from index | `WT_MODIFIED` |
| tracked file deleted | worktree or index records deletion | `WT_DELETED` / `INDEX_DELETED` |
| new untracked file | worktree has a path absent from index | `WT_NEW` |

### Library API

Use [`Repository.status()`](https://www.pygit2.org/index_file.html#pygit2.Repository.status).
It returns a mapping from repository-relative path strings to status flags.
The flags are documented under
[`pygit2.enums.FileStatus`](https://www.pygit2.org/enums.html#pygit2.enums.FileStatus).

The dictionary direction is:

```text
key: repository-relative file path (str)
value: one FileStatus flag or a bitwise combination of FileStatus flags
```

For example, a repository with one edited file and one new file may report:

```python
{
    "README.md": FileStatus.WT_MODIFIED,
    "notes.txt": FileStatus.WT_NEW,
}
```

`FileStatus.CURRENT` is not a collection of the repository's current flags. It
is the zero-valued flag meaning that a particular path has no change. In
practice, `status()` normally omits clean paths, so a clean repository produces
an empty dictionary.

One path can carry a combination of flags. Treat them as a bitmask; do not
write logic that assumes every value equals exactly one nonzero flag. For
example:

```python
combined = FileStatus.INDEX_MODIFIED | FileStatus.WT_MODIFIED
bool(combined & FileStatus.WT_MODIFIED)  # True
```

Equality would not detect one member inside that combination. Bitwise `&`
asks whether a particular flag is present. If Grove's policy is simply "every
change returned by the default `status()` call is dirty," you do not need to
enumerate every individual flag; reason from whether the mapping contains any
changed entry.

The documentation's inspection pattern is:

```python
for filepath, flags in repo.status().items():
    if flags != FileStatus.CURRENT:
        print(filepath)
```

For Grove, the output is a boolean rather than printed paths. Think about
what fact must be true for at least one mapping entry, and what fact an empty
mapping represents.

### Explore status in a REPL

From the repository root, start Python through the project environment:

```sh
uv run python
```

Success looks like a `>>>` prompt. Enter these expressions one at a time:

```python
from pathlib import Path
```

```python
from grove.repo import open_repository
```

```python
from pygit2.enums import FileStatus
```

```python
repo = open_repository(Path.cwd())
```

```python
status = repo.status()
```

```python
status
```

Inspect the path, symbolic flag name, and underlying integer:

```python
[(path, flags.name, flags.value) for path, flags in status.items()]
```

Experiment with a combined flag without changing any files:

```python
combined = FileStatus.INDEX_MODIFIED | FileStatus.WT_MODIFIED
```

```python
bool(combined & FileStatus.WT_MODIFIED)
```

Use `exit()` or Control-D to leave the REPL. Opening `Path.cwd()` here inspects
Grove's own repository, which is useful for learning and does not modify it.

### Grove's dirty policy

Use this policy for Day 1:

- tracked working-tree modifications count as dirty;
- staged changes count as dirty;
- deletions and conflicts count as dirty;
- untracked files count as dirty;
- ignored files do **not** count as dirty.

This matches `Repository.status()` with its defaults: untracked files are
included, ignored files are excluded. It also supports the later restore
safety rule: Grove should not overwrite a user's new untracked file merely
because Git has never tracked it.

Checkpoint inclusion of ignored files is a separate Day 4 design decision.
Do not make `is_dirty` recursively scan the filesystem to solve that future
problem.

### Python concepts exercised

- **Mappings and iteration:** status is a dictionary keyed by relative path.
- **Truth predicates:** `any(...)` can express whether at least one status
  entry represents a change without building an intermediate list.
- **Bit flags:** a flag value can represent several simultaneous conditions.
- **Policy at an API boundary:** pygit2 reports facts; Grove decides which
  facts make an operation unsafe.

### Suggested missing tests

The existing suite covers clean and unstaged modification. Add focused tests
for:

- a staged change;
- a newly created untracked file;
- a deleted tracked file; and
- an ignored file, which should remain clean under the policy above.

Keep each test about one behavior. That makes a failure identify the policy
case that changed.

### Completion check

```sh
uv run pytest tests/test_repo.py::test_clean_repository_is_not_dirty tests/test_repo.py::test_modified_file_makes_it_dirty -v
```

## Recommended implementation loop

Work on one function at a time. After each edit, run the narrowest relevant
test command shown above. Strict XPASS results are progress while the
module-level marker is still present.

After all functions and any added tests behave correctly, remove this line
from `tests/test_repo.py`:

```python
pytestmark = pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="not implemented")
```

Then run the Day 1 file:

```sh
uv run pytest tests/test_repo.py -v
```

Success means every test in that file is an ordinary `PASSED`, with no
XPASS or XFAIL result.

Next run the type checker:

```sh
uv run mypy
```

Success means `Success: no issues found`.

Finally, check that Day 1 did not disturb the rest of the scaffold:

```sh
uv run pytest
```

Success means the repository tests pass, the already-implemented error tests
pass, and later modules remain expected failures.

## Review checklist

Before considering Day 1 complete, check each statement:

- [ ] Public path values use `pathlib.Path`, not ad hoc string manipulation.
- [ ] A failed discovery raises `NotAGitRepository`.
- [ ] A bare repository raises `RepositoryIsBare`.
- [ ] No `assert` is used for runtime input validation.
- [ ] No bare `except`, `except Exception`, `# type: ignore`, or `cast()` was
      introduced.
- [ ] If a caught library error is translated, the new domain error is raised
      `from err`.
- [ ] The working-tree root comes from `repo.workdir`, not an assumption about
      the location of `repo.path`.
- [ ] Dirty-state logic includes staged and untracked content but excludes
      ignored content.
- [ ] `uv run mypy` passes.
- [ ] The complete test suite has no unexpected failures.

## Primary references

- [pygit2: Repository and discovery](https://www.pygit2.org/repository.html)
- [pygit2: index, working copy, and status](https://www.pygit2.org/index_file.html)
- [pygit2: `FileStatus` enums](https://www.pygit2.org/enums.html#pygit2.enums.FileStatus)
- [Python 3.12: `pathlib`](https://docs.python.org/3.12/library/pathlib.html)
- [Python 3.12: exceptions and exception chaining](https://docs.python.org/3.12/tutorial/errors.html#exception-chaining)
- [Git: repository layout](https://git-scm.com/docs/gitrepository-layout)
- [Git: worktrees](https://git-scm.com/docs/git-worktree)
