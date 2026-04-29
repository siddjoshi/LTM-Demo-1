LTM Demo 1

This repository contains a tiny “long-term memory” (LTM) demo:
- a local JSON-backed memory store
- a CLI for adding/searching/updating memories

## Quickstart

Requires Python 3.12+.

```bash
python ltm.py --help

# add memories
python ltm.py add "Buy milk" --tags home,errands --store ./ltm.json
python ltm.py add "Deploy service" --tags work --pinned --store ./ltm.json

# list and search
python ltm.py list --store ./ltm.json
python ltm.py search buy --store ./ltm.json

# stats
python ltm.py stats --store ./ltm.json
```

The store is persisted to `./ltm.json` by default. Override it with `--store path/to/file.json`.

## Running tests

Uses the standard library `unittest` runner:

```bash
python -m unittest -q
```
