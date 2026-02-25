import os


def get_env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()

    if not raw:
        return default

    if default:
        return raw not in {"false", "0", "no"}

    return raw in {"true", "1", "yes"}


def format_bytes(num_bytes: int | float) -> str:
    """Convert bytes to human-readable IEC format (B, KiB, MiB, GiB, etc.)."""
    value: float = num_bytes
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024:
            return f"{value:.2f}".rstrip("0").rstrip(".") + unit
        value /= 1024
    return f"{value:.2f}".rstrip("0").rstrip(".") + "PiB"


def format_age(seconds: float) -> str:
    """Convert seconds to concise age format (e.g., '5d4h3m')."""
    units = [
        ("d", 86400),
        ("h", 3600),
        ("m", 60),
    ]
    result = []
    remaining = int(seconds)
    for suffix, divisor in units:
        if remaining >= divisor:
            count = remaining // divisor
            result.append(f"{count}{suffix}")
            remaining %= divisor
    if remaining > 0:
        result.append(f"{remaining}s")
    return "".join(result) or "0s"
