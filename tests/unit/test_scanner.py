import time

from age_sweeper.scanner import is_expired, scan


def test_scan_flat(tmp_path):
    (tmp_path / "a.txt").touch()
    (tmp_path / "b.txt").touch()
    files = list(scan(tmp_path, recursive=False))
    assert len(files) == 2


def test_scan_recursive(tmp_path):
    (tmp_path / "a.txt").touch()
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").touch()
    files = list(scan(tmp_path, recursive=True))
    assert len(files) == 2


def test_scan_non_recursive_skips_subdirs(tmp_path):
    (tmp_path / "a.txt").touch()
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").touch()
    files = list(scan(tmp_path, recursive=False))
    assert len(files) == 1
    assert files[0].name == "a.txt"


def test_is_expired(tmp_path):
    f = tmp_path / "old.txt"
    f.touch()
    cutoff = time.time() + 10
    assert is_expired(f, cutoff) is True


def test_is_not_expired(tmp_path):
    f = tmp_path / "new.txt"
    f.touch()
    cutoff = time.time() - 10
    assert is_expired(f, cutoff) is False
