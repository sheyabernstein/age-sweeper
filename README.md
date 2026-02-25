# age-sweeper

File garbage collector based on age — designed for Kubernetes CronJobs.

Deletes files older than a configurable retention period from a target directory. Replaces inline shell scripts in CronJob manifests with a reusable container image.

## Usage

```bash
docker run --rm \
  -e TARGET_DIR=/data/downloads \
  -e RETENTION=7d \
  -v /path/to/data:/data/downloads \
  ghcr.io/<owner>/age-sweeper
```

## Environment Variables

| Variable     | Required | Default | Description                                      |
|-------------|----------|---------|--------------------------------------------------|
| `TARGET_DIR` | yes      |         | Directory to scan for old files                  |
| `RETENTION`  | yes      |         | Max file age, e.g. `7d`, `3h30m`, `1w2d6h` (units: w/d/h/m) |
| `DRY_RUN`    | no       | `false` | Log deletions without removing files             |
| `RECURSIVE`  | no       | `true`  | Recurse into subdirectories                      |
| `CLEAN_EMPTY_DIRS` | no | `true`  | Remove empty directories after file deletion     |
| `LOG_LEVEL`  | no       | `info`  | Logging level (debug, info, warning, error)      |

### Retention Format

Units can be combined in descending order (Flux-style compound durations):

- `30m` — 30 minutes
- `6h` — 6 hours
- `5d` — 5 days
- `2w` — 2 weeks
- `7d3h1m` — 7 days, 3 hours, and 1 minute
- `1w2d` — 1 week and 2 days

## Development

```bash
poetry install
pytest -v --cov
ruff check .
ruff format --check .
```
