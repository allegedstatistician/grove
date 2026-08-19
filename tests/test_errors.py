"""The error hierarchy is already defined, so these pass from day one.

They exist to pin down the contract in rule 8: one base class, and catching
it catches everything grove raises on purpose.
"""

import inspect

import pytest

from grove import errors


def _domain_errors() -> list[type[BaseException]]:
    return [
        obj
        for _, obj in inspect.getmembers(errors, inspect.isclass)
        if issubclass(obj, BaseException) and obj is not errors.GroveError
    ]


def test_there_is_at_least_one_domain_error() -> None:
    assert _domain_errors()


@pytest.mark.parametrize("exc", _domain_errors(), ids=lambda e: e.__name__)
def test_every_error_descends_from_grove_error(exc: type[BaseException]) -> None:
    assert issubclass(exc, errors.GroveError)


@pytest.mark.parametrize("exc", _domain_errors(), ids=lambda e: e.__name__)
def test_catching_the_base_catches_the_subclass(exc: type[BaseException]) -> None:
    with pytest.raises(errors.GroveError):
        raise exc("boom")


def test_grove_error_is_not_a_bare_exception_alias() -> None:
    assert errors.GroveError is not Exception
    assert issubclass(errors.GroveError, Exception)
