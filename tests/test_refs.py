"""Ref naming and round-tripping."""

import pytest

from grove import refs

pytestmark = pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="not implemented")


def test_checkpoint_ref_lives_under_the_grove_namespace() -> None:
    name = refs.checkpoint_ref_name("feature-x", 3)
    assert name.startswith(refs.CHECKPOINT_NAMESPACE)


def test_ref_name_round_trips() -> None:
    name = refs.checkpoint_ref_name("feature-x", 7)
    assert refs.parse_checkpoint_ref(name) == ("feature-x", 7)


def test_ids_sort_numerically_not_lexically() -> None:
    """`10` must come after `9`. Zero-padding or a numeric parse â€” your call."""
    ordered = [refs.parse_checkpoint_ref(refs.checkpoint_ref_name("w", i))[1] for i in (2, 9, 10)]
    assert ordered == sorted(ordered)


def test_parse_rejects_a_foreign_ref() -> None:
    from grove.errors import MalformedCheckpoint

    with pytest.raises(MalformedCheckpoint):
        refs.parse_checkpoint_ref("refs/heads/main")
