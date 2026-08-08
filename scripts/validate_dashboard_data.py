#!/usr/bin/env python3
"""Validate the dashboard CSV/metadata contract without network access."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any


INTEGER_RE = re.compile(r"(?:0|[1-9][0-9]*)\Z")


class ValidationError(ValueError):
    """Raised when a dashboard data set violates its published contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _date(value: Any, field: str) -> date:
    _require(isinstance(value, str) and value != "", f"{field} must be an ISO date string")
    try:
        return date.fromisoformat(value[:10])
    except ValueError as exc:
        raise ValidationError(f"{field} is not an ISO date: {value!r}") from exc


def _monday(value: Any, field: str) -> date:
    parsed = _date(value, field)
    _require(parsed.weekday() == 0, f"{field} must be a Monday: {value!r}")
    return parsed


def _metadata_date(value: Any, field: str) -> None:
    if value is None:
        return
    _date(value, field)


def _validate_package_metadata(packages: Any, package_names: list[str]) -> None:
    _require(isinstance(packages, dict), "metadata.packages must be an object")
    _require(list(packages) == package_names, "metadata.packages must match CSV package columns and order")
    for package in package_names:
        details = packages[package]
        _require(isinstance(details, dict), f"metadata.packages.{package} must be an object")
        _require(isinstance(details.get("exists"), bool), f"metadata.packages.{package}.exists must be boolean")
        for field in ("created", "first_upload"):
            if field in details and details[field] is not None:
                _metadata_date(details[field], f"metadata.packages.{package}.{field}")


def validate_dataset(csv_path: Path, metadata_path: Path) -> dict[str, Any]:
    """Validate one CSV and its adjacent metadata file and return a summary."""

    _require(csv_path.is_file(), f"CSV does not exist: {csv_path}")
    _require(metadata_path.is_file(), f"metadata does not exist: {metadata_path}")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read metadata {metadata_path}: {exc}") from exc

    _require(isinstance(metadata, dict), "metadata root must be an object")
    source = metadata.get("source")
    dataset = metadata.get("dataset")
    _require(isinstance(source, dict), "metadata.source must be an object")
    _require(isinstance(dataset, dict), "metadata.dataset must be an object")
    _require(isinstance(metadata.get("vendor"), str) and metadata["vendor"], "metadata.vendor is required")

    csv_name = dataset.get("csv")
    _require(isinstance(csv_name, str) and Path(csv_name).name == csv_name, "metadata.dataset.csv must be a filename")
    _require(csv_path.name == csv_name, f"CSV filename does not match metadata.dataset.csv: {csv_path.name!r}")

    columns = dataset.get("columns")
    _require(isinstance(columns, list) and columns and all(isinstance(column, str) for column in columns), "metadata.dataset.columns must be a non-empty string list")
    _require(columns[0] == "week_start", "the first CSV column must be week_start")
    _require(len(set(columns)) == len(columns), "CSV columns must be unique")
    package_names = columns[1:]
    _validate_package_metadata(metadata.get("packages"), package_names)

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        _require(reader.fieldnames == columns, f"CSV header does not match metadata columns: {reader.fieldnames!r}")
        rows = list(reader)

    expected_rows = dataset.get("rows")
    _require(isinstance(expected_rows, int) and not isinstance(expected_rows, bool), "metadata.dataset.rows must be an integer")
    _require(len(rows) == expected_rows, f"metadata row count {expected_rows} != CSV row count {len(rows)}")
    _require(rows, "CSV must contain at least one data row")

    week_starts: list[date] = []
    for index, row in enumerate(rows, start=2):
        current = _monday(row.get("week_start"), f"CSV row {index}.week_start")
        if week_starts:
            _require(current == week_starts[-1] + timedelta(days=7), f"CSV weeks are not continuous at row {index}")
        week_starts.append(current)
        for package in package_names:
            value = row.get(package)
            _require(value is not None, f"CSV row {index} is missing column {package}")
            _require(value == "" or INTEGER_RE.fullmatch(value) is not None, f"CSV row {index}.{package} must be a non-negative integer or blank")

    for field in ("first_week_start", "last_week_start"):
        if field in dataset and dataset[field] is not None:
            expected = _date(dataset[field], f"metadata.dataset.{field}")
            actual = week_starts[0] if field == "first_week_start" else week_starts[-1]
            _require(expected == actual, f"metadata.dataset.{field} does not match CSV")

    source_latest_day = source.get("latest_download_day")
    latest_day = _date(source_latest_day, "metadata.source.latest_download_day") if source_latest_day is not None else None
    source_complete = source.get("latest_complete_week_start")
    dataset_complete = dataset.get("latest_complete_week_start")
    _require(source_complete == dataset_complete, "source and dataset complete-week metadata disagree")
    if source_complete is not None:
        complete_week = _monday(source_complete, "latest_complete_week_start")
        _require(complete_week in week_starts, "latest_complete_week_start is not present in the CSV")
        if latest_day is not None:
            _require(complete_week + timedelta(days=6) <= latest_day, "latest_complete_week_start is not complete according to latest_download_day")

    return {
        "vendor": metadata["vendor"],
        "csv": str(csv_path),
        "rows": len(rows),
        "columns": columns,
        "first_week_start": week_starts[0].isoformat(),
        "last_week_start": week_starts[-1].isoformat(),
        "latest_complete_week_start": source_complete,
    }


def validate_root(root: Path) -> list[dict[str, Any]]:
    metadata_dir = root / "public" / "data" / "dev-npm-downloads" / "json"
    data_dir = root / "public" / "data" / "dev-npm-downloads" / "Data"
    metadata_files = sorted(metadata_dir.glob("*_metadata.json"))
    _require(metadata_files, f"no dashboard metadata files found in {metadata_dir}")
    summaries = []
    for metadata_path in metadata_files:
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            csv_name = metadata["dataset"]["csv"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValidationError(f"cannot resolve CSV for {metadata_path}: {exc}") from exc
        _require(isinstance(csv_name, str) and Path(csv_name).name == csv_name, f"invalid CSV filename in {metadata_path}")
        summaries.append(validate_dataset(data_dir / csv_name, metadata_path))
    return summaries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root")
    args = parser.parse_args(argv)
    try:
        summaries = validate_root(args.root.resolve())
    except ValidationError as exc:
        print(f"DATA VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"datasets": summaries, "count": len(summaries)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
