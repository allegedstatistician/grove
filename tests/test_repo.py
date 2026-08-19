"""Repository discovery.

Every test here is marked xfail(strict=True). While the body is
`raise NotImplementedError` the suite stays green; the moment you implement
it correctly the test XPASSes, which pytest reports as a failure telling you
to delete the marker. That is the intended loop.
"""

from pathlib import Path

import pytest

from grove import repo
from grove.errors import NotAGitRepository

pytestmark = pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="not implemented")


def test_discover_finds_the_enclosing_repository(scratch_repo: Path) -> None:
    found = repo.discover_repository(scratch_repo)
    assert found.name == ".git"
    assert found.parent == scratch_repo


def test_discover_walks_up_from_a_subdirectory(scratch_repo: Path) -> None:
    nested = scratch_repo / "a" / "b"
    nested.mkdir(parents=True)
    assert repo.discover_repository(nested).parent == scratch_repo


def test_discover_raises_outside_a_repository(not_a_repo: Path) -> None:
    with pytest.raises(NotAGitRepository):
        repo.discover_repository(not_a_repo)


def test_repository_root_is_the_worktree_not_the_git_dir(scratch_repo: Path) -> None:
    opened = repo.open_repository(scratch_repo)
    assert repo.repository_root(opened) == scratch_repo


def test_clean_repository_is_not_dirty(scratch_repo: Path) -> None:
    assert repo.is_dirty(repo.open_repository(scratch_repo)) is False


def test_modified_file_makes_it_dirty(scratch_repo: Path) -> None:
    (scratch_repo / "README.md").write_text("changed\n", encoding="utf-8")
    assert repo.is_dirty(repo.open_repository(scratch_repo)) is True
