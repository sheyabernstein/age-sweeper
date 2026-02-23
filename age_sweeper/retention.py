import re
from datetime import timedelta

_PATTERN = re.compile(r"^(\d+)(m|h|d|w)$")

_UNITS: dict[str, str] = {
    "m": "minutes",
    "h": "hours",
    "d": "days",
    "w": "weeks",
}


def parse_retention(value: str) -> timedelta:
    match = _PATTERN.match(value.strip())
    if not match:
        raise ValueError(
            f"invalid retention format {value!r}, expected <number><unit> where unit is m/h/d/w"
        )
    amount = int(match.group(1))
    unit = _UNITS[match.group(2)]
    return timedelta(**{unit: amount})
