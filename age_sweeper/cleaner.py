import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from age_sweeper.config import Config
from age_sweeper.scanner import is_expired, scan

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

    for path in scan(config.target_dir, config.recursive):
        stats.scanned += 1
        try:
            if not is_expired(path, cutoff):
                continue
            stats.matched += 1
            size = path.stat().st_size
            if config.dry_run:
                log.info("DRY RUN: would delete %s (%d bytes)", path, size)
            else:
                path.unlink()
                stats.deleted += 1
                stats.bytes_freed += size
                log.info("deleted %s (%d bytes)", path, size)
        except (OSError, PermissionError) as e:
            stats.errors += 1
            log.warning("failed to process %s: %s", path, e)

    if config.clean_empty_dirs and config.recursive:
        _remove_empty_dirs(config.target_dir, config.dry_run, stats)

    return stats


def _remove_empty_dirs(target_dir: Path, dry_run: bool, stats: Stats) -> None:
    # Walk bottom-up so children are removed before parents
    for dirpath in sorted(target_dir.rglob("*"), reverse=True):
        if not dirpath.is_dir():
            continue
        if dirpath.parent == target_dir:
            log.debug("ignoring top-level dir %s", dirpath)
            continue
        try:
            if any(dirpath.iterdir()):
                continue
            if dry_run:
                log.info("DRY RUN: would remove empty dir %s", dirpath)
            else:
                dirpath.rmdir()
                stats.dirs_removed += 1
                log.info("removed empty dir %s", dirpath)
        except (OSError, PermissionError) as e:
            stats.errors += 1
            log.warning("failed to remove dir %s: %s", dirpath, e)
