"""Shared PyPI weekly downloads dashboard builder.

Used by: build_livekit_pypi_dashboard.py, build_agora_pypi_dashboard.py
Extracts ClickHouse query, PyPI metadata fetch, CSV, and metadata JSON logic.
"""

from __future__ import annotations

import csv
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CLICKHOUSE_ENDPOINT = "https://sql-clickhouse.clickhouse.com/"
PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"


@dataclass
class PyPIMeta:
    name: str
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
    display_name: str
    packages: list[str]
    csv_path: Path
    html_path: Path
    meta_path: Path
    package_roles: dict[str, str] = field(default_factory=dict)
    package_notes: dict[str, str] = field(default_factory=dict)
    package_colors: dict[str, str] = field(default_factory=dict)
    source_note: str = ""
    interpretation: str = ""
    user_agent: str = "codex-pypi-weekly-dashboard/1.0"


# ── HTTP / ClickHouse ──────────────────────────────────────────────────────

def fetch_url(url: str, *, data: bytes | None = None, accept: str = "application/json",
              user_agent: str = "codex-pypi-weekly-dashboard/1.0", retries: int = 5) -> str:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, data=data, headers={
                "Accept": accept,
                "Content-Type": "text/plain; charset=utf-8",
                "User-Agent": user_agent,
            })
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt < retries - 1:
                time.sleep(2.5 * (attempt + 1))
                last_error = exc
                continue
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:800]}") from exc
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            break
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def fetch_json(url: str, **kwargs) -> dict:
    return json.loads(fetch_url(url, **kwargs))


def clickhouse_csv(sql: str, *, user_agent: str = "codex-pypi-weekly-dashboard/1.0") -> list[dict[str, str]]:
    url = f"{CLICKHOUSE_ENDPOINT}?{urllib.parse.urlencode({'user': 'demo'})}"
    text = fetch_url(url, data=sql.encode("utf-8"), accept="text/csv", user_agent=user_agent)
    return list(csv.DictReader(io.StringIO(text)))


def sql_string_list(values: list[str]) -> str:
    return ", ".join("'" + v.replace("'", "\\'") + "'" for v in values)


# ── PyPI metadata ──────────────────────────────────────────────────────────

def load_pypi_meta(package: str, *, user_agent: str = "codex-pypi-weekly-dashboard/1.0") -> PyPIMeta:
    url = PYPI_JSON_URL.format(package=urllib.parse.quote(package, safe=""))
    try:
        payload = fetch_json(url, user_agent=user_agent)
    except Exception as exc:  # noqa: BLE001
        return PyPIMeta(name=package, exists=False, error=str(exc))

    info = payload.get("info", {})
    first_upload: date | None = None
    for files in payload.get("releases", {}).values():
        for file_info in files:
            raw = file_info.get("upload_time_iso_8601") or file_info.get("upload_time")
            if not raw:
                continue
            try:
                uploaded = datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
            except ValueError:
                continue
            if first_upload is None or uploaded < first_upload:
                first_upload = uploaded

    project_urls = info.get("project_urls") or {}
    source_url = (project_urls.get("Source") or project_urls.get("Homepage")
                  or project_urls.get("Repository") or info.get("home_page"))

    return PyPIMeta(
        name=package, exists=True,
        summary=info.get("summary"),
        latest_version=info.get("version"),
        requires_python=info.get("requires_python"),
        first_upload=first_upload,
        package_url=info.get("package_url") or info.get("project_url"),
        source_url=source_url,
    )


# ── ClickHouse download queries ────────────────────────────────────────────

def latest_pypi_download_day(*, user_agent: str = "codex-pypi-weekly-dashboard/1.0") -> date:
    sql = "SELECT toString(max(date)) AS d FROM pypi.pypi_downloads_per_day FORMAT CSVWithNames"
    rows = clickhouse_csv(sql, user_agent=user_agent)
    return date.fromisoformat(rows[0]["d"])


def fetch_pypi_weekly_downloads(packages: list[str], *, user_agent: str = "codex-pypi-weekly-dashboard/1.0") -> list[dict[str, str]]:
    pkg_list = sql_string_list(packages)
    sql = f"""
SELECT toString(toMonday(date)) AS week_start, project, sum(count) AS downloads
FROM pypi.pypi_downloads_per_day
WHERE project IN ({pkg_list})
GROUP BY week_start, project
ORDER BY week_start, project
FORMAT CSVWithNames""".strip()
    return clickhouse_csv(sql, user_agent=user_agent)


# ── CSV generation ─────────────────────────────────────────────────────────

def build_pypi_rows(raw_rows: list[dict[str, str]], packages: list[str]) -> list[dict[str, int | str]]:
    weekly: dict[tuple[date, str], int] = {}
    week_values: list[date] = []
    for row in raw_rows:
        ws = date.fromisoformat(row["week_start"])
        weekly[(ws, row["project"])] = int(row["downloads"])
        week_values.append(ws)
    if not week_values:
        return []
    rows: list[dict[str, int | str]] = []
    cursor = min(week_values)
    end = max(week_values)
    while cursor <= end:
        out: dict[str, int | str] = {"week_start": cursor.isoformat()}
        for pkg in packages:
            out[pkg] = weekly.get((cursor, pkg), 0)
        rows.append(out)
        cursor += timedelta(days=7)
    return rows


def write_pypi_csv(rows: list[dict[str, int | str]], csv_path: Path, packages: list[str]) -> None:
    columns = ["week_start", *packages]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row[c] for c in columns})


def latest_complete_index(rows: list[dict[str, int | str]], latest_day: date) -> int:
    for idx in range(len(rows) - 1, -1, -1):
        ws = date.fromisoformat(str(rows[idx]["week_start"]))
        if ws + timedelta(days=6) <= latest_day:
            return idx
    return max(0, len(rows) - 1)


# ── Metadata JSON ──────────────────────────────────────────────────────────

def write_pypi_metadata(metas: dict[str, PyPIMeta], rows: list[dict[str, int | str]],
                        latest_day: date, config: PyPIConfig) -> None:
    ci = latest_complete_index(rows, latest_day)
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "vendor": config.vendor,
        "source": {
            "download_table": "pypi.pypi_downloads_per_day",
            "download_provider": "ClickPy public ClickHouse endpoint",
            "download_endpoint": CLICKHOUSE_ENDPOINT,
            "metadata_provider": "PyPI JSON API",
            "source_last_date": latest_day.isoformat(),
            "weekly_grain": "Monday-start weeks",
            "html_chart_policy": "HTML line charts use complete-week metrics; CSV retains all weekly aggregates.",
        },
        "dataset": {
            "csv": config.csv_path.name,
            "html": config.html_path.name,
            "rows": len(rows),
            "first_week_start": str(rows[0]["week_start"]) if rows else None,
            "last_week_start": str(rows[-1]["week_start"]) if rows else None,
            "latest_complete_week_start": str(rows[ci]["week_start"]) if rows else None,
            "columns": ["week_start", *config.packages],
        },
        "packages": {
            pkg: {
                "exists": metas[pkg].exists,
                "role": config.package_roles.get(pkg, ""),
                "summary": metas[pkg].summary,
                "latest_version": metas[pkg].latest_version,
                "requires_python": metas[pkg].requires_python,
                "first_upload": metas[pkg].first_upload.isoformat() if metas[pkg].first_upload else None,
                "package_url": metas[pkg].package_url,
                "source_url": metas[pkg].source_url,
                "note": config.package_notes.get(pkg, ""),
                "error": metas[pkg].error,
            }
            for pkg in config.packages
        },
    }
    config.meta_path.parent.mkdir(parents=True, exist_ok=True)
    config.meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Entry point ────────────────────────────────────────────────────────────

def run_pypi(config: PyPIConfig) -> dict:
    """Run the full PyPI dashboard update pipeline."""
    metas = {p: load_pypi_meta(p, user_agent=config.user_agent) for p in config.packages}
    latest_day = latest_pypi_download_day(user_agent=config.user_agent)
    raw_rows = fetch_pypi_weekly_downloads(config.packages, user_agent=config.user_agent)
    rows = build_pypi_rows(raw_rows, config.packages)

    config.csv_path.parent.mkdir(parents=True, exist_ok=True)
    write_pypi_csv(rows, config.csv_path, config.packages)
    write_pypi_metadata(metas, rows, latest_day, config)

    # Generate HTML via shared pypi dashboard pages
    try:
        from build_pypi_dashboard_pages import build_page
        config.html_path.parent.mkdir(parents=True, exist_ok=True)
        config.html_path.write_text(build_page(config.html_path.name, latest_day.isoformat()), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"warning: shared PyPI dashboard template unavailable: {exc}")

    return {
        "csv": str(config.csv_path),
        "html": str(config.html_path),
        "metadata": str(config.meta_path),
        "rows": len(rows),
        "source_last_date": latest_day.isoformat(),
    }
