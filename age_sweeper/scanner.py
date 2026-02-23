from collections.abc import Iterator
from pathlib import Path


def scan(target_dir: Path, recursive: bool) -> Iterator[Path]:
    if recursive:
        for item in target_dir.rglob("*"):
            if item.is_file():
                yield item
    else:
        for item in target_dir.iterdir():
            if item.is_file():
                yield item


def is_expired(path: Path, cutoff: float) -> bool:
    return path.stat().st_mtime < cutoff
