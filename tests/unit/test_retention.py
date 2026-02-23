from datetime import timedelta

import pytest

from age_sweeper.retention import parse_retention


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("30m", timedelta(minutes=30)),
        ("6h", timedelta(hours=6)),
        ("5d", timedelta(days=5)),
        ("2w", timedelta(weeks=2)),
    ],
)
def test_valid_retention(value: str, expected: timedelta):
    assert parse_retention(value) == expected


@pytest.mark.parametrize("value", ["", "5", "d", "5x", "5.5d", "abc", "-1d"])
def test_invalid_retention(value: str):
    with pytest.raises(ValueError):
        parse_retention(value)
