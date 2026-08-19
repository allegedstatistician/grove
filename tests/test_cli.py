"""CLI surface: exit codes and argument wiring, not business logic."""

import pytest

from grove import cli

pytestmark = pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="not implemented")


def test_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--help"])
    assert exc.value.code == cli.EXIT_OK


def test_no_subcommand_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main([])
    assert exc.value.code == cli.EXIT_USAGE


def test_unknown_subcommand_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["nonsense"])
    assert exc.value.code == cli.EXIT_USAGE


@pytest.mark.parametrize(
    "argv",
    [
        ["new", "feature-x"],
        ["list"],
        ["rm", "feature-x"],
        ["save", "-m", "wip"],
        ["log"],
        ["restore", "0"],
        ["prune", "--keep", "3"],
    ],
    ids=lambda a: a[0],
)
def test_every_subcommand_parses(argv: list[str]) -> None:
    """Probing the public parse_args surface, not argparse internals."""
    assert cli.build_parser().parse_args(argv) is not None


def test_save_message_flag_parses() -> None:
    args = cli.build_parser().parse_args(["save", "-m", "wip"])
    assert args.message == "wip"
