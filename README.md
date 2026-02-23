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
| `RETENTION`  | yes      |         | Max file age: `<number><unit>` (m/h/d/w)         |
| `DRY_RUN`    | no       | `false` | Log deletions without removing files             |
| `RECURSIVE`  | no       | `true`  | Recurse into subdirectories                      |
| `CLEAN_EMPTY_DIRS` | no | `true`  | Remove empty directories after file deletion     |
| `LOG_LEVEL`  | no       | `info`  | Logging level (debug, info, warning, error)      |

### Retention Format

- `30m` — 30 minutes
- `6h` — 6 hours
- `5d` — 5 days
- `2w` — 2 weeks

## Development

```bash
poetry install
pytest -v --cov
ruff check .
ruff format --check .
```
