import os


def get_env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()

    if not raw:
        return default

    if default:
        return raw not in {"false", "0", "no"}

    return raw in {"true", "1", "yes"}
