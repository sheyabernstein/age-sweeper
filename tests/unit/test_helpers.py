import pytest

from age_sweeper.helpers import get_env_bool


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
