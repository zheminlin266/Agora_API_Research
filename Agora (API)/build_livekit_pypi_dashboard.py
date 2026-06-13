from __future__ import annotations

import csv
import html
import io
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


PACKAGES = ["livekit", "livekit-api", "livekit-agents", "livekit-plugins"]
CSV_COLUMNS = ["week_start", *PACKAGES]

PACKAGE_ROLES = {
    "livekit": "Python SDK",
    "livekit-api": "Server API",
    "livekit-agents": "Agents",
    "livekit-plugins": "Plugins",
}

PACKAGE_NOTES = {
    "livekit": "Realtime audio/video/data Python SDK; useful as the broad SDK adoption signal.",
    "livekit-api": "Server API and token generation package; closer to backend deployment activity.",
    "livekit-agents": "Voice/AI agents framework; the key package for LiveKit's AI application momentum.",
    "livekit-plugins": "Small meta/package signal; treat as early-stage noise unless volume becomes sustained.",
}

PACKAGE_COLORS = {
    "livekit": "#126c73",
    "livekit-api": "#a45a2a",
    "livekit-agents": "#5661a6",
    "livekit-plugins": "#805a7a",
}

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "livekit_pypi_weekly_downloads.csv"
HTML_PATH = ROOT / "livekit_pypi_downloads_dashboard.html"
META_PATH = ROOT / "livekit_pypi_downloads_metadata.json"

CLICKHOUSE_ENDPOINT = "https://sql-clickhouse.clickhouse.com/"
PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"


@dataclass
class PackageMeta:
    name: str
    exists: bool
    summary: str | None = None
    latest_version: str | None = None
    requires_python: str | None = None
    first_upload: date | None = None
    package_url: str | None = None
    source_url: str | None = None
    error: str | None = None


def fetch_url(url: str, *, data: bytes | None = None, accept: str = "application/json", retries: int = 5) -> str:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Accept": accept,
                    "Content-Type": "text/plain; charset=utf-8",
                    "User-Agent": "codex-livekit-pypi-weekly-dashboard/1.0",
                },
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt < retries - 1:
                time.sleep(2.5 * (attempt + 1))
                last_error = exc
                continue
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:800]}") from exc
        except Exception as exc:  # noqa: BLE001 - compact retry wrapper for public data calls.
            last_error = exc
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            break
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def fetch_json(url: str) -> dict:
    return json.loads(fetch_url(url))


def clickhouse_csv(sql: str) -> list[dict[str, str]]:
    url = f"{CLICKHOUSE_ENDPOINT}?{urllib.parse.urlencode({'user': 'demo'})}"
    text = fetch_url(url, data=sql.encode("utf-8"), accept="text/csv")
    return list(csv.DictReader(io.StringIO(text)))


def sql_string_list(values: list[str]) -> str:
    return ", ".join("'" + value.replace("'", "\\'") + "'" for value in values)


def load_package_meta(package: str) -> PackageMeta:
    url = PYPI_JSON_URL.format(package=urllib.parse.quote(package, safe=""))
    try:
        payload = fetch_json(url)
    except Exception as exc:  # noqa: BLE001 - keep the dashboard build resilient to metadata hiccups.
        return PackageMeta(name=package, exists=False, error=str(exc))

    info = payload.get("info", {})
    first_upload: date | None = None
    for files in payload.get("releases", {}).values():
        for file_info in files:
            raw = file_info.get("upload_time_iso_8601") or file_info.get("upload_time")
            if not raw:
                continue
            normalized = raw.replace("Z", "+00:00")
            try:
                uploaded = datetime.fromisoformat(normalized).date()
            except ValueError:
                continue
            if first_upload is None or uploaded < first_upload:
                first_upload = uploaded

    project_urls = info.get("project_urls") or {}
    source_url = (
        project_urls.get("Source")
        or project_urls.get("Homepage")
        or project_urls.get("Repository")
        or info.get("home_page")
    )

    return PackageMeta(
        name=package,
        exists=True,
        summary=info.get("summary"),
        latest_version=info.get("version"),
        requires_python=info.get("requires_python"),
        first_upload=first_upload,
        package_url=info.get("package_url") or info.get("project_url"),
        source_url=source_url,
    )


def latest_download_day() -> date:
    sql = """
SELECT toString(max(date)) AS source_last_date
FROM pypi.pypi_downloads_per_day
FORMAT CSVWithNames
""".strip()
    rows = clickhouse_csv(sql)
    return date.fromisoformat(rows[0]["source_last_date"])


def fetch_weekly_downloads() -> list[dict[str, str]]:
    packages = sql_string_list(PACKAGES)
    sql = f"""
SELECT
    toString(toMonday(date)) AS week_start,
    project,
    sum(count) AS downloads
FROM pypi.pypi_downloads_per_day
WHERE project IN ({packages})
GROUP BY week_start, project
ORDER BY week_start, project
FORMAT CSVWithNames
""".strip()
    return clickhouse_csv(sql)


def date_range_weeks(start: date, end: date) -> list[date]:
    weeks: list[date] = []
    cursor = start
    while cursor <= end:
        weeks.append(cursor)
        cursor += timedelta(days=7)
    return weeks


def build_rows(raw_rows: list[dict[str, str]]) -> list[dict[str, int | str]]:
    weekly: dict[tuple[date, str], int] = {}
    week_values: list[date] = []
    for row in raw_rows:
        week_start = date.fromisoformat(row["week_start"])
        package = row["project"]
        downloads = int(row["downloads"])
        weekly[(week_start, package)] = downloads
        week_values.append(week_start)

    if not week_values:
        return []

    rows: list[dict[str, int | str]] = []
    for week_start in date_range_weeks(min(week_values), max(week_values)):
        out: dict[str, int | str] = {"week_start": week_start.isoformat()}
        for package in PACKAGES:
            out[package] = weekly.get((week_start, package), 0)
        rows.append(out)
    return rows


def write_csv(rows: list[dict[str, int | str]]) -> None:
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in CSV_COLUMNS})


def parse_week(row: dict[str, int | str]) -> date:
    return date.fromisoformat(str(row["week_start"]))


def row_total(row: dict[str, int | str]) -> int:
    return sum(int(row[package]) for package in PACKAGES)


def latest_complete_index(rows: list[dict[str, int | str]], latest_day: date) -> int:
    for idx in range(len(rows) - 1, -1, -1):
        if parse_week(rows[idx]) + timedelta(days=6) <= latest_day:
            return idx
    return max(0, len(rows) - 1)


def moving_average(values: list[float], window: int) -> list[float | None]:
    output: list[float | None] = []
    for idx in range(len(values)):
        start = idx - window + 1
        if start < 0:
            output.append(None)
            continue
        output.append(sum(values[start : idx + 1]) / window)
    return output


def fmt(value: float | int) -> str:
    return f"{int(round(value)):,}"


def fmt_compact(value: float | int) -> str:
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}k"
    return f"{value:.0f}"


def pct_change(current: float, prior: float) -> float | None:
    if prior == 0:
        return None
    return current / prior - 1


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:+.1f}%"


def series_points(values: list[float | None], *, width: int, height: int, left: int, top: int, y_max: float) -> str:
    if not values or y_max <= 0:
        return ""
    chart_width = width - left - 24
    chart_height = height - top - 40
    usable = [(idx, value) for idx, value in enumerate(values) if value is not None]
    if not usable:
        return ""
    denom = max(1, len(values) - 1)
    parts = []
    for idx, value in usable:
        x = left + chart_width * idx / denom
        y = top + chart_height * (1 - float(value) / y_max)
        parts.append(f"{x:.1f},{y:.1f}")
    return " ".join(parts)


def y_axis_ticks(y_max: float) -> list[float]:
    if y_max <= 0:
        return [0]
    raw_step = y_max / 4
    magnitude = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude
    if normalized <= 1:
        nice = 1
    elif normalized <= 2:
        nice = 2
    elif normalized <= 5:
        nice = 5
    else:
        nice = 10
    step = nice * magnitude
    top = math.ceil(y_max / step) * step
    return [top - step * i for i in range(5)]


def line_chart_svg(
    rows: list[dict[str, int | str]],
    series: list[dict[str, object]],
    *,
    title: str,
    subtitle: str,
    height: int = 330,
) -> str:
    width = 1120
    left = 72
    top = 44
    values_by_key: dict[str, list[float | None]] = {}
    y_max = 0.0
    for item in series:
        key = str(item["key"])
        values: list[float | None] = []
        for row in rows:
            if key == "__total__":
                value = row_total(row)
            elif key == "__ma4__":
                value = None
            else:
                value = int(row[key])
            values.append(float(value) if value is not None else None)
        if key == "__ma4__":
            totals = [float(row_total(row)) for row in rows]
            values = moving_average(totals, 4)
        values_by_key[key] = values
        for value in values:
            if value is not None:
                y_max = max(y_max, value)

    ticks = y_axis_ticks(y_max)
    chart_width = width - left - 24
    chart_height = height - top - 40
    tick_svg = []
    for tick in ticks:
        y = top + chart_height * (1 - tick / ticks[0]) if ticks[0] else top + chart_height
        tick_svg.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width - 24}" y2="{y:.1f}" class="grid"/>'
            f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" class="axis">{html.escape(fmt_compact(tick))}</text>'
        )

    label_indices = sorted({0, len(rows) // 2, len(rows) - 1})
    x_label_svg = []
    for idx in label_indices:
        x = left + chart_width * idx / max(1, len(rows) - 1)
        label = str(rows[idx]["week_start"])[:7]
        x_label_svg.append(f'<text x="{x:.1f}" y="{height - 12}" text-anchor="middle" class="axis">{label}</text>')

    lines = []
    legends = []
    legend_x = left
    for item in series:
        key = str(item["key"])
        color = str(item["color"])
        stroke_width = str(item.get("stroke_width", 2.4))
        dash = ' stroke-dasharray="7 5"' if item.get("dash") else ""
        points = series_points(values_by_key[key], width=width, height=height, left=left, top=top, y_max=ticks[0] or 1)
        if points:
            lines.append(
                f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
                f'stroke-linecap="round" stroke-linejoin="round"{dash}/>'
            )
        label = html.escape(str(item["label"]))
        legends.append(
            f'<g transform="translate({legend_x},22)">'
            f'<line x1="0" y1="0" x2="22" y2="0" stroke="{color}" stroke-width="{stroke_width}"{dash}/>'
            f'<text x="30" y="4" class="legend">{label}</text></g>'
        )
        legend_x += max(126, len(label) * 8 + 54)

    return f"""
<div class="chart-card">
  <div class="chart-title">
    <div>
      <h2>{html.escape(title)}</h2>
      <p>{html.escape(subtitle)}</p>
    </div>
  </div>
  <svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">
    <text x="0" y="20" class="sr-label">{html.escape(title)}</text>
    {''.join(legends)}
    <line x1="{left}" y1="{top}" x2="{left}" y2="{height - 40}" class="axis-line"/>
    <line x1="{left}" y1="{height - 40}" x2="{width - 24}" y2="{height - 40}" class="axis-line"/>
    {''.join(tick_svg)}
    {''.join(x_label_svg)}
    {''.join(lines)}
  </svg>
</div>
""".strip()


def share_bars(rows: list[dict[str, int | str]], complete_idx: int) -> str:
    row = rows[complete_idx]
    total = row_total(row)
    pieces = []
    for package in PACKAGES:
        value = int(row[package])
        share = value / total if total else 0
        pieces.append(
            f'<div class="share-row">'
            f'<div class="share-label"><span class="dot" style="background:{PACKAGE_COLORS[package]}"></span>'
            f'<span>{html.escape(package)}</span></div>'
            f'<div class="share-track"><span style="width:{share * 100:.2f}%; background:{PACKAGE_COLORS[package]}"></span></div>'
            f'<div class="share-value">{fmt(value)} <small>{share * 100:.1f}%</small></div>'
            f'</div>'
        )
    return "\n".join(pieces)


def recent_table(rows: list[dict[str, int | str]], complete_idx: int, weeks: int = 12) -> str:
    start = max(0, complete_idx - weeks + 1)
    body_rows = []
    for row in rows[start : complete_idx + 1]:
        cells = "".join(f"<td>{fmt(int(row[package]))}</td>" for package in PACKAGES)
        body_rows.append(f"<tr><th>{html.escape(str(row['week_start']))}</th><td>{fmt(row_total(row))}</td>{cells}</tr>")
    headers = "".join(f"<th>{html.escape(package)}</th>" for package in PACKAGES)
    return f"""
<table>
  <thead><tr><th>week_start</th><th>total</th>{headers}</tr></thead>
  <tbody>{''.join(body_rows)}</tbody>
</table>
""".strip()


def package_cards(rows: list[dict[str, int | str]], metas: dict[str, PackageMeta], complete_idx: int) -> str:
    cards = []
    trailing_start = max(0, complete_idx - 11)
    prior_start = max(0, trailing_start - 12)
    for package in PACKAGES:
        latest = int(rows[complete_idx][package])
        avg4_start = max(0, complete_idx - 3)
        avg4 = sum(int(row[package]) for row in rows[avg4_start : complete_idx + 1]) / (complete_idx - avg4_start + 1)
        trailing = sum(int(row[package]) for row in rows[trailing_start : complete_idx + 1])
        prior = sum(int(row[package]) for row in rows[prior_start:trailing_start])
        change = pct_change(trailing, prior) if trailing_start > 0 else None
        meta = metas[package]
        summary = meta.summary or PACKAGE_NOTES[package]
        package_link = (
            f'<a href="{html.escape(meta.package_url)}">PyPI</a>'
            if meta.exists and meta.package_url
            else '<span class="package-status">PyPI 404</span>'
        )
        cards.append(
            f"""
<article class="package-card">
  <div class="package-head">
    <div>
      <h3><span class="dot" style="background:{PACKAGE_COLORS[package]}"></span>{html.escape(package)}</h3>
      <p>{html.escape(PACKAGE_ROLES[package])}</p>
    </div>
    {package_link}
  </div>
  <p class="package-summary">{html.escape(summary)}</p>
  <div class="metrics compact">
    <div><span>Latest full week</span><strong>{fmt(latest)}</strong></div>
    <div><span>4w avg</span><strong>{fmt(avg4)}</strong></div>
    <div><span>12w vs prior</span><strong>{fmt_pct(change)}</strong></div>
    <div><span>Latest version</span><strong>{html.escape(meta.latest_version or 'n/a')}</strong></div>
  </div>
</article>
""".strip()
        )
    return "\n".join(cards)


def build_html(rows: list[dict[str, int | str]], metas: dict[str, PackageMeta], latest_day: date) -> str:
    if not rows:
        raise RuntimeError("No rows returned for dashboard.")

    complete_idx = latest_complete_index(rows, latest_day)
    complete_row = rows[complete_idx]
    complete_week = str(complete_row["week_start"])
    current_week = str(rows[-1]["week_start"])
    first_week = str(rows[0]["week_start"])
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    totals = [row_total(row) for row in rows]
    cumulative = sum(totals)
    latest_total = totals[complete_idx]
    avg4_start = max(0, complete_idx - 3)
    avg4 = sum(totals[avg4_start : complete_idx + 1]) / (complete_idx - avg4_start + 1)
    trailing_start = max(0, complete_idx - 11)
    prior_start = max(0, trailing_start - 12)
    trailing = sum(totals[trailing_start : complete_idx + 1])
    prior = sum(totals[prior_start:trailing_start])
    trailing_change = pct_change(trailing, prior) if trailing_start > 0 else None
    leader = max(PACKAGES, key=lambda package: int(complete_row[package]))
    leader_share = int(complete_row[leader]) / latest_total if latest_total else 0

    total_chart = line_chart_svg(
        rows,
        [
            {"key": "__total__", "label": "Total weekly downloads", "color": "#126c73", "stroke_width": 2.8},
            {"key": "__ma4__", "label": "4-week moving average", "color": "#a45a2a", "stroke_width": 2.4, "dash": True},
        ],
        title="Total PyPI Downloads",
        subtitle="All four packages combined; latest source week may be incomplete.",
    )
    package_chart = line_chart_svg(
        rows,
        [
            {"key": package, "label": package, "color": PACKAGE_COLORS[package], "stroke_width": 2.2}
            for package in PACKAGES
        ],
        title="Package-Level Weekly Downloads",
        subtitle="Weekly package pull volume from ClickPy / PyPI download telemetry.",
    )

    data_json = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    meta_json = json.dumps(
        {
            package: {
                "role": PACKAGE_ROLES[package],
                "summary": metas[package].summary,
                "latest_version": metas[package].latest_version,
                "first_upload": metas[package].first_upload.isoformat() if metas[package].first_upload else None,
            }
            for package in PACKAGES
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LiveKit PyPI Weekly Downloads Dashboard</title>
  <style>
    :root {{
      --bg: #f5f7fa;
      --surface: #ffffff;
      --surface-soft: #fafbfc;
      --ink: #1f242b;
      --muted: #68717d;
      --faint: #8a94a3;
      --line: #dfe5ec;
      --line-soft: #edf1f5;
      --teal: #126c73;
      --copper: #a45a2a;
      --indigo: #5661a6;
      --plum: #805a7a;
      --green: #287a4b;
      --red: #b84949;
      --shadow: 0 10px 28px rgba(31, 36, 43, 0.07);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--bg);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "Microsoft YaHei", Arial, sans-serif;
      font-size: 14px;
    }}
    .shell {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
    header {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 24px;
      box-shadow: var(--shadow);
    }}
    .label {{
      color: var(--teal);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    h1 {{ margin: 6px 0 8px; font-size: 34px; line-height: 1.12; letter-spacing: 0; }}
    h2, h3, p {{ margin: 0; }}
    .lede {{ max-width: 960px; color: var(--muted); line-height: 1.6; }}
    .source-line {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; color: var(--muted); }}
    .source-line span {{
      border: 1px solid var(--line);
      background: var(--surface-soft);
      border-radius: 999px;
      padding: 6px 10px;
      white-space: nowrap;
    }}
    .metrics {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }}
    .metrics div {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 8px; }}
    .metrics strong {{ display: block; font-size: 22px; line-height: 1.1; }}
    .grid-2 {{ display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.55fr); gap: 16px; margin-top: 16px; }}
    .chart-card, .panel, .package-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    .chart-card {{ padding: 18px 18px 12px; overflow: hidden; }}
    .chart-title {{ display: flex; justify-content: space-between; gap: 16px; margin-bottom: 8px; }}
    .chart-title h2, .panel h2 {{ font-size: 18px; margin-bottom: 4px; }}
    .chart-title p, .panel p {{ color: var(--muted); line-height: 1.5; }}
    .chart {{ display: block; width: 100%; height: auto; }}
    .axis {{ fill: var(--muted); font-size: 12px; }}
    .legend {{ fill: var(--ink); font-size: 12px; }}
    .grid {{ stroke: var(--line-soft); stroke-width: 1; }}
    .axis-line {{ stroke: var(--line); stroke-width: 1; }}
    .sr-label {{ fill: transparent; font-size: 1px; }}
    .panel {{ padding: 18px; }}
    .share-row {{ display: grid; grid-template-columns: 140px minmax(0, 1fr) 132px; gap: 12px; align-items: center; margin-top: 14px; }}
    .share-label {{ display: flex; gap: 8px; align-items: center; min-width: 0; }}
    .share-label span:last-child {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex: 0 0 auto; }}
    .share-track {{ height: 10px; border-radius: 999px; background: var(--line-soft); overflow: hidden; }}
    .share-track span {{ display: block; height: 100%; border-radius: 999px; }}
    .share-value {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .share-value small {{ color: var(--muted); }}
    .package-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-top: 16px; }}
    .package-card {{ padding: 18px; }}
    .package-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }}
    .package-head h3 {{ display: flex; gap: 8px; align-items: center; font-size: 17px; }}
    .package-head p {{ color: var(--muted); margin-top: 4px; }}
    a {{ color: var(--teal); text-decoration: none; font-weight: 650; }}
    a:hover {{ text-decoration: underline; }}
    .package-status {{ color: var(--red); font-size: 12px; font-weight: 700; white-space: nowrap; }}
    .package-summary {{ color: var(--muted); line-height: 1.55; min-height: 44px; margin-top: 12px; }}
    .compact {{ grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 14px; }}
    .compact div {{ box-shadow: none; padding: 10px; }}
    .compact strong {{ font-size: 16px; overflow-wrap: anywhere; }}
    .note {{
      border-left: 4px solid var(--copper);
      background: var(--surface-soft);
      padding: 12px 14px;
      color: var(--muted);
      line-height: 1.55;
      margin-top: 14px;
    }}
    .table-wrap {{ overflow-x: auto; margin-top: 16px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 760px; background: var(--surface); }}
    th, td {{ border-bottom: 1px solid var(--line-soft); padding: 10px 8px; text-align: right; font-variant-numeric: tabular-nums; }}
    th:first-child, td:first-child {{ text-align: left; }}
    thead th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }}
    tbody th {{ font-weight: 600; }}
    footer {{ color: var(--muted); line-height: 1.6; margin: 18px 2px 0; font-size: 12px; }}
    @media (max-width: 980px) {{
      .shell {{ padding: 16px; }}
      h1 {{ font-size: 28px; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .grid-2, .package-grid {{ grid-template-columns: 1fr; }}
      .share-row {{ grid-template-columns: 1fr; gap: 6px; }}
      .share-value {{ text-align: left; }}
    }}
    @media (max-width: 640px) {{
      .metrics, .compact {{ grid-template-columns: 1fr; }}
      header, .chart-card, .panel, .package-card {{ padding: 14px; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div class="label">LiveKit / PyPI Weekly Downloads</div>
      <h1>LiveKit Python Package Download Signals</h1>
      <p class="lede">跟踪 livekit、livekit-api、livekit-agents、livekit-plugins 四个 PyPI 包的周度下载量，用于观察 Python SDK、服务端 API 与 Agents 生态的开发者需求变化。下载量代表包拉取次数，不等于唯一开发者、活跃应用或付费客户。</p>
      <div class="source-line">
        <span>数据周数：{len(rows)}</span>
        <span>周度范围：{html.escape(first_week)} 至 {html.escape(current_week)}</span>
        <span>源表最新日期：{latest_day.isoformat()}</span>
        <span>最新完整周：{html.escape(complete_week)}</span>
      </div>
      <section class="metrics" aria-label="summary metrics">
        <div><span>累计下载</span><strong>{fmt(cumulative)}</strong></div>
        <div><span>最新完整周合计</span><strong>{fmt(latest_total)}</strong></div>
        <div><span>合计 4 周均值</span><strong>{fmt(avg4)}</strong></div>
        <div><span>12 周 vs 前 12 周</span><strong>{fmt_pct(trailing_change)}</strong></div>
        <div><span>最新完整周第一</span><strong>{html.escape(leader)} · {leader_share * 100:.1f}%</strong></div>
      </section>
    </header>

    <section class="grid-2">
      {total_chart}
      <aside class="panel">
        <h2>Latest Full Week Mix</h2>
        <p>{html.escape(complete_week)} 周内各包下载占比。</p>
        {share_bars(rows, complete_idx)}
        <div class="note">`livekit`、`livekit-api` 与 `livekit-agents` 体量接近时，通常说明 SDK、后端接入和 Agent 框架拉取需求在同步扩大；`livekit-plugins` 目前基数极小，应主要看是否出现连续放量。</div>
      </aside>
    </section>

    <section style="margin-top:16px">
      {package_chart}
    </section>

    <section class="package-grid">
      {package_cards(rows, metas, complete_idx)}
    </section>

    <section class="panel" style="margin-top:16px">
      <h2>Recent Complete Weeks</h2>
      <p>最近 12 个完整周的原始 CSV 周度数据切片。</p>
      <div class="table-wrap">{recent_table(rows, complete_idx)}</div>
    </section>

    <footer>
      Data source: ClickPy public ClickHouse table pypi.pypi_downloads_per_day; package metadata from PyPI JSON API.
      Generated: {html.escape(generated_at)}. CSV file: livekit_pypi_weekly_downloads.csv.
    </footer>
  </main>
  <script type="application/json" id="weekly-download-data">{data_json}</script>
  <script type="application/json" id="package-metadata">{meta_json}</script>
</body>
</html>
"""


def write_metadata(metas: dict[str, PackageMeta], rows: list[dict[str, int | str]], latest_day: date) -> None:
    complete_idx = latest_complete_index(rows, latest_day)
    metadata = {
        "source": {
            "download_table": "pypi.pypi_downloads_per_day",
            "download_provider": "ClickPy public ClickHouse endpoint",
            "download_endpoint": CLICKHOUSE_ENDPOINT,
            "metadata_provider": "PyPI JSON API",
            "source_last_date": latest_day.isoformat(),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "packages": {
            package: {
                "exists": metas[package].exists,
                "role": PACKAGE_ROLES[package],
                "summary": metas[package].summary,
                "latest_version": metas[package].latest_version,
                "requires_python": metas[package].requires_python,
                "first_upload": metas[package].first_upload.isoformat() if metas[package].first_upload else None,
                "package_url": metas[package].package_url,
                "source_url": metas[package].source_url,
                "note": PACKAGE_NOTES[package],
                "error": metas[package].error,
            }
            for package in PACKAGES
        },
        "dataset": {
            "csv": CSV_PATH.name,
            "html": HTML_PATH.name,
            "rows": len(rows),
            "first_week_start": rows[0]["week_start"],
            "last_week_start": rows[-1]["week_start"],
            "latest_complete_week_start": rows[complete_idx]["week_start"],
            "columns": CSV_COLUMNS,
        },
    }
    META_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    metas = {package: load_package_meta(package) for package in PACKAGES}
    latest_day = latest_download_day()
    raw_rows = fetch_weekly_downloads()
    rows = build_rows(raw_rows)
    write_csv(rows)
    write_metadata(metas, rows, latest_day)
    try:
        from build_pypi_dashboard_pages import build_page

        HTML_PATH.write_text(build_page(HTML_PATH.name, latest_day.isoformat()), encoding="utf-8")
    except Exception as exc:
        HTML_PATH.write_text(build_html(rows, metas, latest_day), encoding="utf-8")
        print(f"warning: shared PyPI dashboard template unavailable; wrote legacy dashboard: {exc}")
    print(
        json.dumps(
            {
                "csv": str(CSV_PATH),
                "html": str(HTML_PATH),
                "metadata": str(META_PATH),
                "rows": len(rows),
                "source_last_date": latest_day.isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
