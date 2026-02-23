import os
import subprocess
import tempfile
import time
from uuid import uuid4

import pytest

IMAGE = f"age-sweeper:e2e-{str(uuid4())[:8]}"


@pytest.fixture(scope="module", autouse=True)
def docker_image():
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    subprocess.run(["docker", "build", "-t", IMAGE, root], check=True, capture_output=True)
    yield
    subprocess.run(["docker", "rmi", IMAGE], check=False, capture_output=True)


def _run(env: dict[str, str], volume_src: str) -> subprocess.CompletedProcess:
    cmd = ["docker", "run", "--rm", "-v", f"{volume_src}:/data"]
    for k, v in env.items():
        cmd.extend(["-e", f"{k}={v}"])
    cmd.append(IMAGE)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def _make_old_file(path: str, age_seconds: int = 86400 * 10):
    with open(path, "w") as f:
        f.write("old data")
    old_time = time.time() - age_seconds
    os.utime(path, (old_time, old_time))


def _make_new_file(path: str, content: str = "fresh data"):
    with open(path, "w") as f:
        f.write(content)


@pytest.mark.e2e
def test_deletes_old_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        old = os.path.join(tmpdir, "old.txt")
        new = os.path.join(tmpdir, "new.txt")
        _make_old_file(old)
        _make_new_file(new)

        result = _run({"TARGET_DIR": "/data", "RETENTION": "5d"}, tmpdir)
        assert result.returncode == 0
        assert not os.path.exists(old)
        assert os.path.exists(new)
        assert "deleted" in result.stderr.lower()


@pytest.mark.e2e
def test_dry_run_keeps_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        old = os.path.join(tmpdir, "old.txt")
        _make_old_file(old)

        result = _run({"TARGET_DIR": "/data", "RETENTION": "5d", "DRY_RUN": "true"}, tmpdir)
        assert result.returncode == 0
        assert os.path.exists(old)
        assert "dry run" in result.stderr.lower()


@pytest.mark.e2e
def test_keeps_top_level_dirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        subdir = os.path.join(tmpdir, "subdir")
        os.makedirs(subdir)
        _make_old_file(os.path.join(subdir, "old.txt"))

        result = _run({"TARGET_DIR": "/data", "RETENTION": "5d"}, tmpdir)
        assert result.returncode == 0
        assert os.path.exists(subdir)
        assert not os.path.exists(os.path.join(subdir, "old.txt"))
        assert "empty dir" not in result.stderr.lower()


@pytest.mark.e2e
def test_removes_nested_empty_dirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        nested = os.path.join(tmpdir, "subdir", "nested")
        os.makedirs(nested)
        _make_old_file(os.path.join(nested, "old.txt"))

        result = _run({"TARGET_DIR": "/data", "RETENTION": "5d"}, tmpdir)
        assert result.returncode == 0
        assert os.path.exists(os.path.join(tmpdir, "subdir"))
        assert not os.path.exists(nested)
        assert "empty dir" in result.stderr.lower()


@pytest.mark.e2e
def test_missing_env_vars():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _run({"TARGET_DIR": "/data"}, tmpdir)
        assert result.returncode != 0
        assert "RETENTION" in result.stderr
