import pytest

from age_sweeper.config import load_config


def test_missing_target_dir(monkeypatch):
    monkeypatch.delenv("TARGET_DIR", raising=False)
    monkeypatch.setenv("RETENTION", "5d")
    with pytest.raises(SystemExit):
        load_config()


def test_empty_target_dir(monkeypatch):
    monkeypatch.setenv("TARGET_DIR", "")
    monkeypatch.setenv("RETENTION", "5d")
    with pytest.raises(SystemExit):
        load_config()


def test_root_target_dir(monkeypatch):
    monkeypatch.setenv("TARGET_DIR", "/")
    monkeypatch.setenv("RETENTION", "5d")
    with pytest.raises(SystemExit):
        load_config()


def test_missing_retention(monkeypatch, tmp_path):
    monkeypatch.setenv("TARGET_DIR", str(tmp_path))
    monkeypatch.delenv("RETENTION", raising=False)
    with pytest.raises(SystemExit):
        load_config()


def test_invalid_retention(monkeypatch, tmp_path):
    monkeypatch.setenv("TARGET_DIR", str(tmp_path))
    monkeypatch.setenv("RETENTION", "bad")
    with pytest.raises(SystemExit):
        load_config()


def test_nonexistent_target_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("TARGET_DIR", str(tmp_path / "nope"))
    monkeypatch.setenv("RETENTION", "5d")
    with pytest.raises(SystemExit):
        load_config()


def test_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("TARGET_DIR", str(tmp_path))
    monkeypatch.setenv("RETENTION", "5d")
    monkeypatch.delenv("DRY_RUN", raising=False)
    monkeypatch.delenv("RECURSIVE", raising=False)
    monkeypatch.delenv("CLEAN_EMPTY_DIRS", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    config = load_config()
    assert config.target_dir == tmp_path
    assert config.dry_run is False
    assert config.recursive is True
    assert config.clean_empty_dirs is True
    assert config.log_level == "INFO"


def test_dry_run_true(monkeypatch, tmp_path):
    monkeypatch.setenv("TARGET_DIR", str(tmp_path))
    monkeypatch.setenv("RETENTION", "5d")
    monkeypatch.setenv("DRY_RUN", "true")
    assert load_config().dry_run is True


def test_recursive_false(monkeypatch, tmp_path):
    monkeypatch.setenv("TARGET_DIR", str(tmp_path))
    monkeypatch.setenv("RETENTION", "5d")
    monkeypatch.setenv("RECURSIVE", "false")
    assert load_config().recursive is False


def test_clean_empty_dirs_false(monkeypatch, tmp_path):
    monkeypatch.setenv("TARGET_DIR", str(tmp_path))
    monkeypatch.setenv("RETENTION", "5d")
    monkeypatch.setenv("CLEAN_EMPTY_DIRS", "false")
    assert load_config().clean_empty_dirs is False
