import os
import sys
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from age_sweeper.helpers import get_env_bool
from age_sweeper.retention import parse_retention


@dataclass(frozen=True)
class Config:
    target_dir: Path
    retention: timedelta
    dry_run: bool
    recursive: bool
    clean_empty_dirs: bool
    log_level: str


def load_config() -> Config:
    target_dir = os.environ.get("TARGET_DIR", "").strip()
    if not target_dir or target_dir == "/":
        print("ERROR: TARGET_DIR must be set and cannot be empty or '/'", file=sys.stderr)
        raise SystemExit(1)

    target_path = Path(target_dir)
    if not target_path.is_dir():
        print(
            f"ERROR: TARGET_DIR {target_dir!r} does not exist or is not a directory",
            file=sys.stderr,
        )
        raise SystemExit(1)

    retention_raw = os.environ.get("RETENTION", "").strip()
    if not retention_raw:
        print("ERROR: RETENTION must be set", file=sys.stderr)
        raise SystemExit(1)

    try:
        retention = parse_retention(retention_raw)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1) from e

    dry_run = get_env_bool("DRY_RUN", default=False)
    recursive = get_env_bool("RECURSIVE", default=True)
    clean_empty_dirs = get_env_bool("CLEAN_EMPTY_DIRS", default=True)
    log_level = os.environ.get("LOG_LEVEL", "info").strip().upper()

    return Config(
        target_dir=target_path,
        retention=retention,
        dry_run=dry_run,
        recursive=recursive,
        clean_empty_dirs=clean_empty_dirs,
        log_level=log_level,
    )
