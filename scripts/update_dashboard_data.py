#!/usr/bin/env python3
"""Refresh the developer-download dashboard from one config registry."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.dashboard_config import DATASETS, DATA_ROOT, DatasetSpec, manifest_payload
from lib.npm_dashboard import latest_download_day as latest_npm_download_day
from lib.npm_dashboard import run as run_npm
from lib.pypi_dashboard import (
    fetch_weekly,
    incremental_query_start,
    latest_download_day as latest_pypi_download_day,
)
from lib.pypi_dashboard import run_pypi


def write_manifest() -> Path:
    """Publish the frontend manifest only after the selected refresh succeeds."""

    path = DATA_ROOT / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".manifest-", suffix=".tmp", dir=path.parent)
    temp_path = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            json.dump(manifest_payload(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)
    return path


def update_npm(specs: list[DatasetSpec], *, rebuild: bool) -> list[dict[str, object]]:
    if not specs:
        return []
    latest_day = latest_npm_download_day(user_agent="codex-dashboard-npm/3.0")
    return [
        run_npm(spec.config(), latest_day=latest_day, rebuild=rebuild)
        for spec in specs
    ]


def update_pypi(specs: list[DatasetSpec], *, rebuild: bool) -> list[dict[str, object]]:
    if not specs:
        return []
    configs = [spec.config() for spec in specs]
    latest_day = latest_pypi_download_day(user_agent="codex-dashboard-pypi/3.0")
    query_start = incremental_query_start(configs, rebuild=rebuild)
    packages = [package for config in configs for package in config.packages]
    raw_rows = fetch_weekly(
        packages,
        user_agent="codex-dashboard-pypi/3.0",
        start=query_start,
        end=latest_day,
    )
    return [
        run_pypi(config, latest_day=latest_day, raw_rows=raw_rows, rebuild=rebuild)
        for config in configs
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        action="append",
        choices=[spec.key for spec in DATASETS],
        help="refresh only this dataset; repeat the option to select several",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="ignore existing CSVs and rebuild the selected datasets from source",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="regenerate the frontend manifest without contacting upstream sources",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.manifest_only:
        print(json.dumps({"manifest": str(write_manifest())}, ensure_ascii=False, indent=2))
        return 0
    selected_keys = set(args.dataset or (spec.key for spec in DATASETS))
    selected = [spec for spec in DATASETS if spec.key in selected_keys]
    npm_specs = [spec for spec in selected if spec.kind == "npm"]
    pypi_specs = [spec for spec in selected if spec.kind == "pypi"]

    summaries = update_npm(npm_specs, rebuild=args.rebuild)
    summaries.extend(update_pypi(pypi_specs, rebuild=args.rebuild))
    manifest_path = write_manifest()
    print(
        json.dumps(
            {
                "datasets": summaries,
                "mode": "rebuild" if args.rebuild else "incremental",
                "manifest": str(manifest_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
