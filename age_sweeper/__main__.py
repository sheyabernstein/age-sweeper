import logging

from age_sweeper.cleaner import clean
from age_sweeper.config import load_config
from age_sweeper.helpers import format_bytes


def main() -> None:
    config = load_config()
    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log = logging.getLogger(__name__)

    log.info(
        "starting: target=%s retention=%s recursive=%s dry_run=%s",
        config.target_dir,
        config.retention,
        config.recursive,
        config.dry_run,
    )

    stats = clean(config)

    log.info(
        "done: scanned=%d matched=%d deleted=%d dirs_removed=%d errors=%d bytes_freed=%s",
        stats.scanned,
        stats.matched,
        stats.deleted,
        stats.dirs_removed,
        stats.errors,
        format_bytes(stats.bytes_freed),
    )


if __name__ == "__main__":
    main()
