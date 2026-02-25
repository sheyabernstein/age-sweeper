import re
from datetime import timedelta

_TOKEN = re.compile(r"(\d+)(w|d|h|m)")

_UNITS: dict[str, str] = {
    "m": "minutes",
    "h": "hours",
    "d": "days",
    "w": "weeks",
}


def parse_retention(value: str) -> timedelta:
    text = value.strip()
    tokens = _TOKEN.findall(text)
    if not tokens:
        raise ValueError(
            f"invalid retention format {value!r}, "
            "expected compound duration like '7d', '3h30m', or '1w2d6h'"
        )
    # Reject if there are characters not covered by the matched tokens
    consumed = "".join(amount + unit for amount, unit in tokens)
    if consumed != text:
        raise ValueError(
            f"invalid retention format {value!r}, "
            "expected compound duration like '7d', '3h30m', or '1w2d6h'"
        )
    kwargs: dict[str, int] = {}
    for amount, unit in tokens:
        key = _UNITS[unit]
        kwargs[key] = kwargs.get(key, 0) + int(amount)
    return timedelta(**kwargs)
