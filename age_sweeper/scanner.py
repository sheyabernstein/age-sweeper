import os
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple


class FileEntry(NamedTuple):
    path: Path
    stat: os.stat_result


def scan(target_dir: Path, recursive: bool) -> Iterator[FileEntry]:
    if recursive:
        for dirpath, _dirnames, filenames in os.walk(target_dir):
            dp = Path(dirpath)
            for name in filenames:
                p = dp / name
                try:
                    yield FileEntry(p, p.stat())
                except OSError:
                    pass
    else:
        with os.scandir(target_dir) as it:
            for entry in it:
                if entry.is_file():
                    p = Path(entry.path)
                    try:
                        yield FileEntry(p, entry.stat())
                    except OSError:
                        pass


def walk_bottom_up(
    target_dir: Path,
) -> Iterator[tuple[Path, list[str], list[FileEntry]]]:
    for dirpath, dirnames, filenames in os.walk(target_dir, topdown=False):
        dp = Path(dirpath)
        file_entries: list[FileEntry] = []
        for name in filenames:
            p = dp / name
            try:
                file_entries.append(FileEntry(p, p.stat()))
            except OSError:
                pass
        yield dp, dirnames, file_entries


def is_expired(path: Path, cutoff: float, *, stat: os.stat_result | None = None) -> bool:
    st = stat if stat is not None else path.stat()
    return st.st_mtime < cutoff
