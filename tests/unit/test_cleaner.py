import os
import time
from datetime import timedelta

from age_sweeper.cleaner import clean
from age_sweeper.config import Config


def _make_old_file(path, age_seconds=86400 * 10):
    path.write_text("data")
    old_time = time.time() - age_seconds
    os.utime(path, (old_time, old_time))


def test_deletes_expired_files(tmp_path):
    _make_old_file(tmp_path / "old.txt")
    (tmp_path / "new.txt").write_text("fresh")

    config = Config(
        target_dir=tmp_path,
        retention=timedelta(days=5),
        dry_run=False,
        recursive=True,
        clean_empty_dirs=False,
        log_level="DEBUG",
    )
    stats = clean(config)

    assert stats.scanned == 2
    assert stats.matched == 1
    assert stats.deleted == 1
    assert stats.bytes_freed == 4
    assert not (tmp_path / "old.txt").exists()
    assert (tmp_path / "new.txt").exists()


def test_dry_run(tmp_path):
    _make_old_file(tmp_path / "old.txt")

    config = Config(
        target_dir=tmp_path,
        retention=timedelta(days=5),
        dry_run=True,
        recursive=True,
        clean_empty_dirs=False,
        log_level="DEBUG",
    )
    stats = clean(config)

    assert stats.matched == 1
    assert stats.deleted == 0
    assert stats.bytes_freed == 0
    assert (tmp_path / "old.txt").exists()


def test_permission_error(tmp_path):
    f = tmp_path / "locked.txt"
    _make_old_file(f)
    os.chmod(tmp_path, 0o555)

    config = Config(
        target_dir=tmp_path,
        retention=timedelta(days=5),
        dry_run=False,
        recursive=True,
        clean_empty_dirs=False,
        log_level="DEBUG",
    )
    stats = clean(config)

    assert stats.errors >= 1
    os.chmod(tmp_path, 0o755)


def test_removes_empty_dirs(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    _make_old_file(sub / "old.txt")

    config = Config(
        target_dir=tmp_path,
        retention=timedelta(days=5),
        dry_run=False,
        recursive=True,
        clean_empty_dirs=True,
        log_level="DEBUG",
    )
    stats = clean(config)

    assert stats.deleted == 1
    assert stats.dirs_removed == 1
    assert not sub.exists()


def test_keeps_nonempty_dirs(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    _make_old_file(sub / "old.txt")
    (sub / "new.txt").write_text("keep")

    config = Config(
        target_dir=tmp_path,
        retention=timedelta(days=5),
        dry_run=False,
        recursive=True,
        clean_empty_dirs=True,
        log_level="DEBUG",
    )
    stats = clean(config)

    assert stats.deleted == 1
    assert stats.dirs_removed == 0
    assert sub.exists()


def test_clean_empty_dirs_disabled(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    _make_old_file(sub / "old.txt")

    config = Config(
        target_dir=tmp_path,
        retention=timedelta(days=5),
        dry_run=False,
        recursive=True,
        clean_empty_dirs=False,
        log_level="DEBUG",
    )
    stats = clean(config)

    assert stats.deleted == 1
    assert stats.dirs_removed == 0
    assert sub.exists()
