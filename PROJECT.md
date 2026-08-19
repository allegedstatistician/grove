# grove â€” spec and plan

## Goal

A CLI that manages git worktrees and lets you snapshot a working tree at any
moment without disturbing git's own state, built so that implementing it
forces me to learn how git stores things.

## Approach

State lives entirely in git refs under `refs/grove/`. A checkpoint is an
ordinary commit object whose tree is built from the current working
directory; the ref pointing at it is the only bookkeeping. `git status`,
`HEAD`, the index, and every branch are untouched by a checkpoint, which is
what separates this from `git stash`. Object-database work goes through
`pygit2`; the three worktree operations shell out to `git worktree` because
the porcelain's admin bookkeeping is fiddly and not the lesson. The decision
most likely to be wrong: **parenting checkpoints on the previous checkpoint
rather than on `HEAD`.** It gives each worktree a clean linear checkpoint
history, but it means a checkpoint commit is not reachable from any branch
and its relationship to real history is implicit rather than recorded.

## Out of scope

Remote operations, async, TUIs, daemons, config files, a plugin system,
partial/hunk-level checkpointing, conflict resolution on restore.

## Open assumptions

- Worktrees are placed as siblings of the repository root. A `.worktrees/`
  subdirectory is the obvious alternative.
- Untracked files *are* included in a checkpoint. This is the opposite of
  what `git stash` does by default and is the whole reason the feature is
  useful, but it means `.gitignore`d junk gets snapshotted too unless
  filtered.
- Checkpoint ids are per-worktree integers starting at 0, not hashes.
- `restore` refuses on a dirty worktree unless `--force`.

## Command surface

```
grove new <name> [--branch BRANCH]   create a worktree
grove list                           list worktrees
grove rm <name> [--force]            remove a worktree
grove save [-m MESSAGE]              checkpoint the current worktree
grove log [--worktree W] [--json]    list checkpoints
grove restore <id> [--force]         restore a checkpoint
grove prune [--keep N]               drop old checkpoints
```

## Week plan

Each day ends when the named tests go from xfail to passing and the
`@pytest.mark.xfail` marker can be deleted.

| Day | Module | Target tests | Git concept |
|----|--------|--------------|-------------|
| 1 | `errors.py`, `repo.py` | `test_errors`, `test_repo` | repository discovery, the `.git` dir vs. the worktree root, status flags |
| 2 | `worktree.py` | `test_worktree` | the worktree admin directory, `--porcelain` output as a stable interface |
| 3 | `refs.py` | `test_refs` | refs as files/packed entries, namespaces, `git check-ref-format` |
| 4 | `checkpoint.py` â€” `save` | first four in `test_checkpoint` | blobs, trees, commits; why a commit is just a pointer to a tree |
| 5 | `checkpoint.py` â€” `list`, `get` | next two | walking refs, reading commit metadata, author vs. committer time |
| 6 | `checkpoint.py` â€” `restore`, `prune` | last two | tree traversal, checkout semantics, reachability and `git gc` |
| 7 | `cli.py` | `test_cli` | nothing git-specific â€” argparse, exit codes, error translation |

## The one decision to make before day 4

Does `save` build its tree with `Index.add_all()` + `Index.write_tree()`, or
by walking the directory and writing blobs by hand with `hashlib` and `zlib`?

The first is three lines and teaches the index. The second is a day of work
and teaches the object format â€” zlib-deflated `"blob <len>\0<content>"`,
SHA-1 over the uncompressed bytes, the `.git/objects/ab/cdef...` fanout. In
Rust this choice barely existed because `flate2` and `sha1` were already
dependencies. In Python both are stdlib, so the hand-rolled path costs
nothing to start. Decide deliberately; it is the difference between a week
of plumbing and a week of API calls.
