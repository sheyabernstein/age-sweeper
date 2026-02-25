from datetime import timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from age_sweeper.retention import parse_retention

_VALID_CASES = [
    ("30m", timedelta(minutes=30)),
    ("6h", timedelta(hours=6)),
    ("5d", timedelta(days=5)),
    ("2w", timedelta(weeks=2)),
    # compound durations
    ("7d3h1m", timedelta(days=7, hours=3, minutes=1)),
    ("1w2d", timedelta(weeks=1, days=2)),
    ("12h30m", timedelta(hours=12, minutes=30)),
    ("2w3d4h5m", timedelta(weeks=2, days=3, hours=4, minutes=5)),
]


@pytest.mark.parametrize(
    ("value", "expected"),
    _VALID_CASES,
    ids=[f"{x}: {y}" for x, y in _VALID_CASES],
)
def test_valid_retention(value: str, expected: timedelta):
    assert parse_retention(value) == expected


@pytest.mark.parametrize("value", ["", "5", "d", "5x", "5.5d", "abc", "-1d", "3d!", "3d 2h"])
def test_invalid_retention(value: str):
    with pytest.raises(ValueError):
        parse_retention(value)


# --- hypothesis property-based tests ---

_UNIT_WEIGHTS = {"w": "weeks", "d": "days", "h": "hours", "m": "minutes"}


@st.composite
def retention_strings(draw):
    """Generate valid single or compound retention strings with expected timedelta."""
    units = list(_UNIT_WEIGHTS.keys())
    # pick 1-4 distinct units in canonical order
    chosen = draw(st.lists(st.sampled_from(units), min_size=1, max_size=4, unique=True))
    chosen.sort(key=units.index)
    parts = []
    kwargs: dict[str, int] = {}
    for u in chosen:
        amount = draw(st.integers(min_value=1, max_value=999))
        parts.append(f"{amount}{u}")
        kwargs[_UNIT_WEIGHTS[u]] = amount
    return "".join(parts), timedelta(**kwargs)


@given(data=retention_strings())
def test_hypothesis_valid_retention(data):
    text, expected = data
    assert parse_retention(text) == expected


@given(text=st.text(max_size=30))
def test_hypothesis_arbitrary_text(text):
    try:
        result = parse_retention(text)
        assert isinstance(result, timedelta)
    except ValueError:
        pass
