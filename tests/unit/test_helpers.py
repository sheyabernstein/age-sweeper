import pytest

from age_sweeper.helpers import format_age, format_bytes, get_env_bool


@pytest.mark.parametrize(
    ("env_val", "default", "expected"),
    [
        # default=False: only truthy values return True
        ("true", False, True),
        ("1", False, True),
        ("yes", False, True),
        ("TRUE", False, True),
        ("false", False, False),
        ("0", False, False),
        ("no", False, False),
        ("random", False, False),
        # default=True: only falsy values return False
        ("false", True, False),
        ("0", True, False),
        ("no", True, False),
        ("FALSE", True, False),
        ("true", True, True),
        ("1", True, True),
        ("yes", True, True),
        ("random", True, True),
        # unset returns default
        ("", False, False),
        ("", True, True),
    ],
)
def test_get_env_bool(monkeypatch, env_val: str, default: bool, expected: bool):
    if env_val:
        monkeypatch.setenv("TEST_BOOL", env_val)
    else:
        monkeypatch.delenv("TEST_BOOL", raising=False)
    assert get_env_bool("TEST_BOOL", default=default) is expected


@pytest.mark.parametrize(
    ("num_bytes", "expected"),
    [
        (0, "0B"),
        (1, "1B"),
        (512, "512B"),
        (1024, "1KB"),
        (1536, "1.5KB"),
        (1024**2, "1MB"),
        (1024**2 * 5 + 1024 * 256, "5.25MB"),
        (1024**3, "1GB"),
        (1024**4, "1TB"),
        (1024**5, "1PB"),
    ],
)
def test_format_bytes(num_bytes, expected):
    assert format_bytes(num_bytes) == expected


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "0s"),
        (30, "30s"),
        (60, "1m"),
        (90, "1m30s"),
        (3600, "1h"),
        (3661, "1h1m1s"),
        (86400, "1d"),
        (86400 * 3 + 3600 * 2, "3d2h"),
        (86400 * 10, "10d"),
        (86400 + 60 * 5, "1d5m"),
    ],
)
def test_format_age(seconds, expected):
    assert format_age(seconds) == expected
