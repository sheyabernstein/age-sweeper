import logging
import time
from collections.abc import Iterable
from dataclasses import dataclass, field

from age_sweeper.config import Config
from age_sweeper.helpers import format_age, format_bytes
from age_sweeper.scanner import FileEntry, is_expired, scan, walk_bottom_up

log = logging.getLogger(__name__)


@dataclass
class Stats:
    scanned: int = 0
    matched: int = 0
    deleted: int = 0
    errors: int = 0
    bytes_freed: int = field(default=0)
    dirs_removed: int = 0


def clean(config: Config) -> Stats:
    stats = Stats()
    cutoff = time.time() - config.retention.total_seconds()
    now = time.time()

    if config.recursive and config.clean_empty_dirs:
        _clean_single_pass(config, stats, cutoff, now)
    else:
        _process_entries(scan(config.target_dir, config.recursive), config, stats, cutoff, now)

    return stats


def _delete_or_log(entry: FileEntry, now: float, dry_run: bool, stats: Stats) -> None:
    size = entry.stat.st_size
    age = now - entry.stat.st_mtime
    if dry_run:
        log.info(
            "DRY RUN: would delete %s (%s, age %s)",
            entry.path,
            format_bytes(size),
            format_age(age),
        )
    else:
        entry.path.unlink()
        stats.deleted += 1
        stats.bytes_freed += size
        log.info(
            "deleted %s (%s, age %s)",
            entry.path,
            format_bytes(size),
            format_age(age),
        )


def _process_entries(
    entries: Iterable[FileEntry], config: Config, stats: Stats, cutoff: float, now: float
) -> None:
    for entry in entries:
        stats.scanned += 1
        try:
            if not is_expired(entry.path, cutoff, stat=entry.stat):
                continue
            stats.matched += 1
            _delete_or_log(entry, now, config.dry_run, stats)
        except (OSError, PermissionError) as e:
            stats.errors += 1
            log.warning("failed to process %s: %s", entry.path, e)


def _clean_single_pass(config: Config, stats: Stats, cutoff: float, now: float) -> None:
    for dirpath, _dirnames, file_entries in walk_bottom_up(config.target_dir):
        _process_entries(file_entries, config, stats, cutoff, now)

        # Empty-dir cleanup: skip target_dir itself and top-level children
        if dirpath == config.target_dir:
            continue
        if dirpath.parent == config.target_dir:
            log.debug("ignoring top-level dir %s", dirpath)
            continue
        try:
            if any(dirpath.iterdir()):
                continue
            age = now - dirpath.stat().st_mtime
            if config.dry_run:
                log.info(
                    "DRY RUN: would remove empty dir %s (age %s)",
                    dirpath,
                    format_age(age),
                )
            else:
                dirpath.rmdir()
                stats.dirs_removed += 1
                log.info("removed empty dir %s (age %s)", dirpath, format_age(age))
        except (OSError, PermissionError) as e:
            stats.errors += 1
            log.warning("failed to remove dir %s: %s", dirpath, e)
