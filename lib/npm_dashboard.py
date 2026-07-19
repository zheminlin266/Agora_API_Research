"""Fetch npm metadata and weekly downloads for the single-page dashboard."""

from __future__ import annotations

import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

NPM_REGISTRY = "https://registry.npmjs.org"
NPM_DOWNLOADS = "https://api.npmjs.org/downloads"
EARLIEST_DOWNLOAD_DATE = date(2015, 1, 10)
MAX_RANGE_DAYS = 548


@dataclass
class PackageMeta:
    exists: bool
    created: date | None = None
    created_raw: str | None = None
    modified_raw: str | None = None
    description: str | None = None
    latest_version: str | None = None
    error: str | None = None


@dataclass
class VendorConfig:
    vendor: str
    packages: list[str]
    csv_path: Path
    meta_path: Path
    user_agent: str = "codex-npm-weekly-dashboard/1.0"


def fetch_json(url: str, *, user_agent: str, retries: int = 6) -> dict:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url, headers={"Accept": "application/json", "User-Agent": user_agent}
            )
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries - 1:
                try:
                    wait = float(exc.headers.get("Retry-After") or 20 * (attempt + 1))
                except ValueError:
                    wait = 20 * (attempt + 1)
                time.sleep(wait)
                continue
            raise
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries - 1:
                time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def parse_iso_date(raw: str) -> date:
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc).date()


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def latest_complete_week(latest_day: date) -> date:
    monday = week_start(latest_day)
    return monday if latest_day >= monday + timedelta(days=6) else monday - timedelta(days=7)


def iter_ranges(start: date, end: date):
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=MAX_RANGE_DAYS - 1), end)
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


def load_package_meta(package: str, *, user_agent: str) -> PackageMeta:
    url = f"{NPM_REGISTRY}/{urllib.parse.quote(package, safe='')}"
    try:
        data = fetch_json(url, user_agent=user_agent)
    except urllib.error.HTTPError as exc:
        return PackageMeta(exists=False, error=f"HTTP {exc.code}: {exc.reason}")
    created_raw = data.get("time", {}).get("created")
    return PackageMeta(
        exists=True,
        created=parse_iso_date(created_raw) if created_raw else None,
        created_raw=created_raw,
        modified_raw=data.get("time", {}).get("modified"),
        description=data.get("description"),
        latest_version=data.get("dist-tags", {}).get("latest"),
    )


def latest_download_day(*, user_agent: str) -> date:
    payload = fetch_json(f"{NPM_DOWNLOADS}/point/last-day", user_agent=user_agent)
    return min(date.fromisoformat(payload["end"]), datetime.now(timezone.utc).date() - timedelta(days=1))


def load_weekly(package: str, start: date, end: date, *, user_agent: str) -> dict[date, int]:
    weekly: dict[date, int] = {}
    encoded = urllib.parse.quote(package, safe="")
    for chunk_start, chunk_end in iter_ranges(start, end):
        period = f"{chunk_start.isoformat()}:{chunk_end.isoformat()}"
        try:
            payload = fetch_json(f"{NPM_DOWNLOADS}/range/{period}/{encoded}", user_agent=user_agent)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise
        time.sleep(0.25)
        for row in payload.get("downloads", []):
            monday = week_start(date.fromisoformat(row["day"]))
            weekly[monday] = weekly.get(monday, 0) + int(row.get("downloads", 0))
    return weekly


def build_rows(
    metas: dict[str, PackageMeta], downloads: dict[str, dict[date, int]], latest_day: date
) -> list[dict[str, str]]:
    starts = [week_start(meta.created) for meta in metas.values() if meta.created]
    if not starts:
        return []
    rows: list[dict[str, str]] = []
    current = min(starts)
    while current <= week_start(latest_day):
        row = {"week_start": current.isoformat()}
        for package, meta in metas.items():
            start = week_start(meta.created) if meta.created else None
            row[package] = "" if start is None or current < start else str(downloads[package].get(current, 0))
        rows.append(row)
        current += timedelta(days=7)
    return rows


def write_outputs(
    rows: list[dict[str, str]], metas: dict[str, PackageMeta], latest_day: date, config: VendorConfig
) -> None:
    columns = ["week_start", *config.packages]
    config.csv_path.parent.mkdir(parents=True, exist_ok=True)
    with config.csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    complete_week = latest_complete_week(latest_day).isoformat()
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "vendor": config.vendor,
        "source": {
            "registry": NPM_REGISTRY,
            "downloads": NPM_DOWNLOADS,
            "weekly_grain": "Monday-start weeks",
            "latest_download_day": latest_day.isoformat(),
            "latest_complete_week_start": complete_week,
            "caveat": "npm counts include automation, mirrors, caches, and dependency installs.",
        },
        "dataset": {
            "csv": config.csv_path.name,
            "rows": len(rows),
            "columns": columns,
            "latest_complete_week_start": complete_week,
        },
        "packages": {
            package: {
                "exists": meta.exists,
                "created": meta.created_raw,
                "modified": meta.modified_raw,
                "latest_version": meta.latest_version,
                "description": meta.description,
                "error": meta.error,
            }
            for package, meta in metas.items()
        },
    }
    config.meta_path.parent.mkdir(parents=True, exist_ok=True)
    config.meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def run(config: VendorConfig) -> dict:
    """Refresh one npm dataset and its metadata."""
    metas = {package: load_package_meta(package, user_agent=config.user_agent) for package in config.packages}
    latest_day = latest_download_day(user_agent=config.user_agent)
    downloads = {
        package: (
            load_weekly(
                package,
                max(meta.created, EARLIEST_DOWNLOAD_DATE),
                latest_day,
                user_agent=config.user_agent,
            )
            if meta.exists and meta.created
            else {}
        )
        for package, meta in metas.items()
    }
    rows = build_rows(metas, downloads, latest_day)
    write_outputs(rows, metas, latest_day, config)
    return {
        "csv": str(config.csv_path),
        "metadata": str(config.meta_path),
        "rows": len(rows),
        "latest_download_day": latest_day.isoformat(),
    }
