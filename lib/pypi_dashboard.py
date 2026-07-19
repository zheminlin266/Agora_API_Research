"""Fetch PyPI metadata and weekly downloads for the single-page dashboard."""

from __future__ import annotations

import csv
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CLICKHOUSE_ENDPOINT = "https://sql-clickhouse.clickhouse.com/"
PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"


@dataclass
class PackageMeta:
    exists: bool
    summary: str | None = None
    latest_version: str | None = None
    requires_python: str | None = None
    first_upload: date | None = None
    package_url: str | None = None
    source_url: str | None = None
    error: str | None = None


@dataclass
class PyPIConfig:
    vendor: str
    packages: list[str]
    csv_path: Path
    meta_path: Path
    user_agent: str = "codex-pypi-weekly-dashboard/1.0"


def fetch_url(
    url: str,
    *,
    data: bytes | None = None,
    accept: str = "application/json",
    user_agent: str,
    retries: int = 5,
) -> str:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url,
                data=data,
                headers={"Accept": accept, "Content-Type": "text/plain; charset=utf-8", "User-Agent": user_agent},
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt < retries - 1:
                last_error = exc
                time.sleep(2.5 * (attempt + 1))
                continue
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:800]}") from exc
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def clickhouse_csv(sql: str, *, user_agent: str) -> list[dict[str, str]]:
    url = f"{CLICKHOUSE_ENDPOINT}?{urllib.parse.urlencode({'user': 'demo'})}"
    text = fetch_url(url, data=sql.encode(), accept="text/csv", user_agent=user_agent)
    return list(csv.DictReader(io.StringIO(text)))


def load_meta(package: str, *, user_agent: str) -> PackageMeta:
    url = PYPI_JSON_URL.format(package=urllib.parse.quote(package, safe=""))
    try:
        payload = json.loads(fetch_url(url, user_agent=user_agent))
    except Exception as exc:  # noqa: BLE001
        return PackageMeta(exists=False, error=str(exc))
    info = payload.get("info", {})
    uploads = []
    for files in payload.get("releases", {}).values():
        for file_info in files:
            raw = file_info.get("upload_time_iso_8601") or file_info.get("upload_time")
            if raw:
                try:
                    uploads.append(datetime.fromisoformat(raw.replace("Z", "+00:00")).date())
                except ValueError:
                    pass
    project_urls = info.get("project_urls") or {}
    return PackageMeta(
        exists=True,
        summary=info.get("summary"),
        latest_version=info.get("version"),
        requires_python=info.get("requires_python"),
        first_upload=min(uploads) if uploads else None,
        package_url=info.get("package_url") or info.get("project_url"),
        source_url=(
            project_urls.get("Source")
            or project_urls.get("Repository")
            or project_urls.get("Homepage")
            or info.get("home_page")
        ),
    )


def latest_download_day(*, user_agent: str) -> date:
    sql = "SELECT toString(max(date)) AS d FROM pypi.pypi_downloads_per_day FORMAT CSVWithNames"
    return date.fromisoformat(clickhouse_csv(sql, user_agent=user_agent)[0]["d"])


def fetch_weekly(packages: list[str], *, user_agent: str) -> list[dict[str, str]]:
    values = ", ".join("'" + package.replace("'", "\\'") + "'" for package in packages)
    sql = f"""
SELECT toString(toMonday(date)) AS week_start, project, sum(count) AS downloads
FROM pypi.pypi_downloads_per_day
WHERE project IN ({values})
GROUP BY week_start, project
ORDER BY week_start, project
FORMAT CSVWithNames""".strip()
    return clickhouse_csv(sql, user_agent=user_agent)


def build_rows(raw_rows: list[dict[str, str]], packages: list[str]) -> list[dict[str, int | str]]:
    weekly = {
        (date.fromisoformat(row["week_start"]), row["project"]): int(row["downloads"])
        for row in raw_rows
    }
    if not weekly:
        return []
    weeks = [week for week, _ in weekly]
    rows = []
    current = min(weeks)
    while current <= max(weeks):
        rows.append({
            "week_start": current.isoformat(),
            **{package: weekly.get((current, package), 0) for package in packages},
        })
        current += timedelta(days=7)
    return rows


def complete_week(rows: list[dict[str, int | str]], latest_day: date) -> str | None:
    for row in reversed(rows):
        monday = date.fromisoformat(str(row["week_start"]))
        if monday + timedelta(days=6) <= latest_day:
            return monday.isoformat()
    return None


def write_outputs(
    rows: list[dict[str, int | str]], metas: dict[str, PackageMeta], latest_day: date, config: PyPIConfig
) -> None:
    columns = ["week_start", *config.packages]
    config.csv_path.parent.mkdir(parents=True, exist_ok=True)
    with config.csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    latest_complete = complete_week(rows, latest_day)
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "vendor": config.vendor,
        "source": {
            "download_table": "pypi.pypi_downloads_per_day",
            "download_provider": "ClickPy public ClickHouse endpoint",
            "metadata_provider": "PyPI JSON API",
            "source_last_date": latest_day.isoformat(),
            "weekly_grain": "Monday-start weeks",
            "latest_complete_week_start": latest_complete,
        },
        "dataset": {
            "csv": config.csv_path.name,
            "rows": len(rows),
            "first_week_start": str(rows[0]["week_start"]) if rows else None,
            "last_week_start": str(rows[-1]["week_start"]) if rows else None,
            "latest_complete_week_start": latest_complete,
            "columns": columns,
        },
        "packages": {
            package: {
                "exists": meta.exists,
                "summary": meta.summary,
                "latest_version": meta.latest_version,
                "requires_python": meta.requires_python,
                "first_upload": meta.first_upload.isoformat() if meta.first_upload else None,
                "package_url": meta.package_url,
                "source_url": meta.source_url,
                "error": meta.error,
            }
            for package, meta in metas.items()
        },
    }
    config.meta_path.parent.mkdir(parents=True, exist_ok=True)
    config.meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def run_pypi(config: PyPIConfig) -> dict:
    """Refresh one PyPI dataset and its metadata."""
    metas = {package: load_meta(package, user_agent=config.user_agent) for package in config.packages}
    latest_day = latest_download_day(user_agent=config.user_agent)
    rows = build_rows(fetch_weekly(config.packages, user_agent=config.user_agent), config.packages)
    write_outputs(rows, metas, latest_day, config)
    return {
        "csv": str(config.csv_path),
        "metadata": str(config.meta_path),
        "rows": len(rows),
        "source_last_date": latest_day.isoformat(),
    }
