from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


CLICKHOUSE_URL = "https://sql-clickhouse.clickhouse.com/?user=play"
TARGET_DIR = ""
CSV_NAME = "agora_pypi_weekly_downloads.csv"
DASHBOARD_NAME = "agora_pypi_weekly_downloads_dashboard.html"

PACKAGES = [
    ("agora-token-builder", "agora_token_builder_downloads", "token_builder"),
    ("agora-python-server-sdk", "agora_python_server_sdk_downloads", "server_sdk"),
    ("agora-python-sdk", "agora_python_sdk_downloads", "python_sdk"),
    ("agora-realtime-ai-api-v1", "agora_realtime_ai_api_v1_downloads", "realtime_ai"),
]


def post_query(sql: str) -> str:
    req = urllib.request.Request(
        CLICKHOUSE_URL,
        data=sql.encode("utf-8"),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read().decode("utf-8")


def parse_tsv_with_names(text: str) -> list[dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    headers = lines[0].split("\t")
    return [dict(zip(headers, line.split("\t"))) for line in lines[1:]]


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def each_week(start: date, end: date):
    current = monday_of(start)
    last = monday_of(end)
    while current <= last:
        yield current
        current += timedelta(days=7)


def sql_project_list() -> str:
    return ",".join(f"'{project}'" for project, _, _ in PACKAGES)


def fetch_summary() -> dict[str, dict[str, date | int]]:
    sql = f"""
SELECT
  project,
  min(date) AS first_date,
  max(date) AS last_date,
  sum(count) AS total_downloads,
  count() AS active_days
FROM pypi.pypi_downloads_per_day
WHERE project IN ({sql_project_list()})
GROUP BY project
ORDER BY project
FORMAT TSVWithNames
"""
    result: dict[str, dict[str, date | int]] = {}
    for row in parse_tsv_with_names(post_query(sql)):
        result[row["project"]] = {
            "first_date": date.fromisoformat(row["first_date"]),
            "last_date": date.fromisoformat(row["last_date"]),
            "total_downloads": int(row["total_downloads"]),
            "active_days": int(row["active_days"]),
        }
    missing = [project for project, _, _ in PACKAGES if project not in result]
    if missing:
        raise RuntimeError(f"No ClickPy rows found for: {', '.join(missing)}")
    return result


def fetch_weekly() -> dict[tuple[str, date], int]:
    sql = f"""
SELECT
  project,
  toStartOfWeek(date, 1)::Date AS week,
  sum(count) AS downloads
FROM pypi.pypi_downloads_per_day
WHERE project IN ({sql_project_list()})
GROUP BY project, week
ORDER BY project, week
FORMAT TSVWithNames
"""
    result: dict[tuple[str, date], int] = {}
    for row in parse_tsv_with_names(post_query(sql)):
        result[(row["project"], date.fromisoformat(row["week"]))] = int(row["downloads"])
    return result


def build_rows() -> tuple[list[dict[str, int | str]], dict[str, dict[str, date | int]]]:
    summary = fetch_summary()
    weekly = fetch_weekly()
    first_date = min(details["first_date"] for details in summary.values())
    last_date = max(details["last_date"] for details in summary.values())

    rows: list[dict[str, int | str]] = []
    for week in each_week(first_date, last_date):  # type: ignore[arg-type]
        row: dict[str, int | str] = {"week_start": week.isoformat()}
        for project, csv_col, _js_key in PACKAGES:
            row[csv_col] = weekly.get((project, week), 0)
        rows.append(row)
    return rows, summary


def write_csv(rows: list[dict[str, int | str]], path: Path) -> None:
    fieldnames = ["week_start"] + [csv_col for _project, csv_col, _js_key in PACKAGES]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def dashboard_data(rows: list[dict[str, int | str]]) -> list[dict[str, int | str]]:
    output: list[dict[str, int | str]] = []
    for row in rows:
        item: dict[str, int | str] = {"week_start": row["week_start"]}
        for _project, csv_col, js_key in PACKAGES:
            item[js_key] = int(row[csv_col])
        output.append(item)
    return output


def ensure_complete_week_chart_rule(html: str) -> str:
    if "const CHART_DATA = DATA.slice(0, completeIdx + 1);" not in html:
        html = html.replace(
            "    const completeIdx = latestCompleteIndex();\n\n    function selectedRows()",
            "    const completeIdx = latestCompleteIndex();\n"
            "    const CHART_DATA = DATA.slice(0, completeIdx + 1);\n\n"
            "    function selectedRows()",
        )
    html = html.replace('if (state.range === "all") return DATA;', 'if (state.range === "all") return CHART_DATA;')
    html = html.replace(
        "return DATA.slice(Math.max(0, DATA.length - count));",
        "return CHART_DATA.slice(Math.max(0, CHART_DATA.length - count));",
    )
    html = html.replace(
        'state.range === "all" ? `${DATA[0].week_start} 至 ${DATA[DATA.length - 1].week_start}`',
        'state.range === "all" ? `${CHART_DATA[0].week_start} 至 ${CHART_DATA[CHART_DATA.length - 1].week_start}`',
    )
    return html


def update_dashboard(path: Path, rows: list[dict[str, int | str]], source_last_date: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Dashboard template not found: {path}")

    html = path.read_text(encoding="utf-8")
    data_json = json.dumps(dashboard_data(rows), ensure_ascii=False, separators=(",", ":"))
    replacement = f'const DATA = {data_json};\n    const SOURCE_LAST_DATE = "{source_last_date}";'
    html, count = re.subn(
        r'const DATA = \[.*?\];\s*const SOURCE_LAST_DATE = "[^"]*";',
        replacement,
        html,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Could not replace dashboard DATA/SOURCE_LAST_DATE block.")

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = re.sub(
        r"Generated: [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2} UTC\.",
        f"Generated: {generated}.",
        html,
    )
    html = ensure_complete_week_chart_rule(html)
    path.write_text(html, encoding="utf-8")


def resolve_target_dir(repo: Path, target_dir: str) -> Path:
    if (repo / DASHBOARD_NAME).exists() or (repo / CSV_NAME).exists():
        return repo
    return repo / target_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Update Agora PyPI weekly CSV and dashboard.")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root or target folder.")
    parser.add_argument("--target-dir", default=TARGET_DIR, help="Folder under repo root.")
    parser.add_argument("--skip-dashboard", action="store_true", help="Only write CSV.")
    args = parser.parse_args()

    target = resolve_target_dir(args.repo.resolve(), args.target_dir)
    target.mkdir(parents=True, exist_ok=True)

    rows, summary = build_rows()
    source_last = max(details["last_date"] for details in summary.values()).isoformat()  # type: ignore[union-attr]
    write_csv(rows, target / CSV_NAME)
    if not args.skip_dashboard:
        update_dashboard(target / DASHBOARD_NAME, rows, source_last)

    latest_week = rows[-1]["week_start"] if rows else "n/a"
    source_last_day = date.fromisoformat(source_last)
    source_last_monday = monday_of(source_last_day)
    complete_week = (
        source_last_monday
        if source_last_day >= source_last_monday + timedelta(days=6)
        else source_last_monday - timedelta(days=7)
    ).isoformat()
    print(f"Wrote {target / CSV_NAME}")
    if not args.skip_dashboard:
        print(f"Updated {target / DASHBOARD_NAME}")
    print(f"Rows: {len(rows)}; source_last_date: {source_last}; latest_complete_week: {complete_week}; latest_row_week: {latest_week}")


if __name__ == "__main__":
    main()
