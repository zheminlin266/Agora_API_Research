"""Shared npm weekly downloads dashboard builder.

Used by: build_agora_npm_dashboard.py, build_livekit_npm_dashboard.py,
         build_vendor_npm_dashboards.py (replaces .mjs)

Extracts the common data-fetch, aggregation, CSV, and chart-component logic
that was previously duplicated across each vendor script.
"""

from __future__ import annotations

import csv
import html
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

NPM_REGISTRY = "https://registry.npmjs.org"
NPM_DOWNLOADS = "https://api.npmjs.org/downloads"
EARLIEST_NPM_DOWNLOAD_DATE = date(2015, 1, 10)
MAX_RANGE_DAYS = 548
DEFAULT_COLORS = ["#2563eb", "#d97706", "#0f766e", "#be123c", "#475569", "#7c3aed", "#0891b2"]


@dataclass
class PackageMeta:
    name: str
    exists: bool
    created: date | None = None
    created_raw: str | None = None
    modified_raw: str | None = None
    description: str | None = None
    latest_version: str | None = None
    error: str | None = None


@dataclass
class SectionGroup:
    title: str
    subtitle: str
    packages: list[str]


@dataclass
class VendorConfig:
    vendor: str
    display_name: str
    packages: list[str]
    csv_path: Path
    html_path: Path
    meta_path: Path
    colors: dict[str, str] = field(default_factory=dict)
    package_notes: dict[str, str] = field(default_factory=dict)
    package_descriptions: dict[str, str] = field(default_factory=dict)
    derived_columns: dict[str, list[str]] = field(default_factory=dict)
    chart_series: list[str] = field(default_factory=list)
    section_groups: list[SectionGroup] = field(default_factory=list)
    lang: str = "en"
    include_latest_version: bool = True
    user_agent: str = "codex-npm-weekly-dashboard/1.0"


# ── Utility functions ──────────────────────────────────────────────────────

def fetch_json(url: str, *, user_agent: str = "codex-npm-weekly-dashboard/1.0", retries: int = 6) -> dict:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": user_agent})
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries - 1:
                retry_after = exc.headers.get("Retry-After")
                try:
                    wait_seconds = float(retry_after) if retry_after else 20 * (attempt + 1)
                except ValueError:
                    wait_seconds = 20 * (attempt + 1)
                time.sleep(wait_seconds)
                continue
            raise
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def url_package(package: str) -> str:
    return urllib.parse.quote(package, safe="")


def parse_iso_date(raw: str) -> date:
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc).date()


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def iter_ranges(start: date, end: date):
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=MAX_RANGE_DAYS - 1), end)
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


def format_int(value: int | float | None) -> str:
    if value is None:
        return "-"
    return f"{int(value):,}"


def compact_int(value: int | float | None) -> str:
    if value is None:
        return "-"
    value = float(value)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return str(int(value))


def nice_y_max(max_value: int) -> int:
    if max_value <= 0:
        return 1
    exponent = math.floor(math.log10(max_value))
    base = 10 ** exponent
    for multiplier in (1, 2, 5, 10):
        candidate = multiplier * base
        if candidate >= max_value:
            return int(candidate)
    return int(10 * base)


def latest_complete_week_start(latest_day: date) -> date:
    current_week = week_start(latest_day)
    if latest_day >= current_week + timedelta(days=6):
        return current_week
    return current_week - timedelta(days=7)


def get_color(config: VendorConfig, package: str, index: int) -> str:
    if package in config.colors:
        return config.colors[package]
    return DEFAULT_COLORS[index % len(DEFAULT_COLORS)]


# ── API functions ──────────────────────────────────────────────────────────

def load_package_meta(package: str, *, user_agent: str = "codex-npm-weekly-dashboard/1.0") -> PackageMeta:
    try:
        data = fetch_json(f"{NPM_REGISTRY}/{url_package(package)}", user_agent=user_agent)
    except urllib.error.HTTPError as exc:
        return PackageMeta(name=package, exists=False, error=f"HTTP {exc.code}: {exc.reason}")
    created_raw = data.get("time", {}).get("created")
    return PackageMeta(
        name=package, exists=True,
        created=parse_iso_date(created_raw) if created_raw else None,
        created_raw=created_raw,
        modified_raw=data.get("time", {}).get("modified"),
        description=data.get("description"),
        latest_version=data.get("dist-tags", {}).get("latest"),
    )


def latest_download_day() -> date:
    data = fetch_json(f"{NPM_DOWNLOADS}/point/last-day")
    endpoint_day = date.fromisoformat(data["end"])
    yesterday_utc = datetime.now(timezone.utc).date() - timedelta(days=1)
    return max(endpoint_day, yesterday_utc)


def load_daily_downloads(package: str, start: date, end: date, *, user_agent: str = "codex-npm-weekly-dashboard/1.0") -> dict[date, int]:
    daily: dict[date, int] = {}
    for chunk_start, chunk_end in iter_ranges(start, end):
        period = f"{chunk_start.isoformat()}:{chunk_end.isoformat()}"
        url = f"{NPM_DOWNLOADS}/range/{period}/{url_package(package)}"
        try:
            payload = fetch_json(url, user_agent=user_agent)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise
        time.sleep(0.25)
        for row in payload.get("downloads", []):
            daily[date.fromisoformat(row["day"])] = int(row.get("downloads", 0))
    return daily


def weekly_from_daily(daily: dict[date, int]) -> dict[date, int]:
    weekly: dict[date, int] = {}
    for day, downloads in daily.items():
        start = week_start(day)
        weekly[start] = weekly.get(start, 0) + downloads
    return weekly


# ── CSV generation ─────────────────────────────────────────────────────────

def get_csv_columns(config: VendorConfig) -> list[str]:
    if config.chart_series:
        all_cols = ["week_start"]
        seen = set()
        for col in config.chart_series:
            if col not in seen:
                all_cols.append(col)
                seen.add(col)
        return all_cols
    cols = ["week_start", *config.packages]
    for derived in config.derived_columns:
        cols.append(derived)
    return cols


def build_csv_rows(metas: dict[str, PackageMeta], weekly_data: dict[str, dict[date, int]], latest_day: date, config: VendorConfig) -> list[dict[str, str]]:
    starts = [week_start(meta.created) for meta in metas.values() if meta.exists and meta.created is not None]
    if not starts:
        return []
    first_week = min(starts)
    last_week = week_start(latest_day)
    package_start_weeks = {p: week_start(m.created) if m.created else None for p, m in metas.items()}
    rows: list[dict[str, str]] = []
    current = first_week
    while current <= last_week:
        row: dict[str, str] = {"week_start": current.isoformat()}
        for package in config.packages:
            meta = metas[package]
            start_week = package_start_weeks.get(package)
            if not meta.exists or start_week is None or current < start_week:
                row[package] = ""
            else:
                row[package] = str(weekly_data.get(package, {}).get(current, 0))
        for derived_name, sources in config.derived_columns.items():
            row[derived_name] = str(sum(int(row.get(s, 0) or 0) for s in sources))
        rows.append(row)
        current += timedelta(days=7)
    return rows


def write_csv(rows: list[dict[str, str]], csv_path: Path, columns: list[str]) -> None:
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def series_for_package(rows: list[dict[str, str]], package: str, complete_through: date | None = None) -> list[tuple[str, int]]:
    series = []
    for row in rows:
        row_week = date.fromisoformat(row["week_start"])
        if complete_through is not None and row_week > complete_through:
            continue
        value = row.get(package, "")
        if value != "":
            series.append((row["week_start"], int(value)))
    return series


# ── Chart components ───────────────────────────────────────────────────────

def chart_payload(series: list[tuple[str, int]]) -> str:
    payload = [{"week": week, "downloads": value} for week, value in series]
    return html.escape(json.dumps(payload, ensure_ascii=False), quote=True)


def interactive_chart_shell(package: str, series: list[tuple[str, int]], color: str) -> str:
    safe_package = html.escape(package)
    data = chart_payload(series)
    min_week = html.escape(series[0][0]) if series else ""
    max_week = html.escape(series[-1][0]) if series else ""
    disabled = " disabled" if not series else ""
    return f"""
      <div class="chart-toolbar">
        <label>
          <span>Start week</span>
          <input class="range-start" type="date" min="{min_week}" max="{max_week}" value="{min_week}" aria-label="Start week for {safe_package}"{disabled}>
        </label>
        <label>
          <span>End week</span>
          <input class="range-end" type="date" min="{min_week}" max="{max_week}" value="{max_week}" aria-label="End week for {safe_package}"{disabled}>
        </label>
      </div>
      <div class="chart-wrap" data-chart data-package="{safe_package}" data-color="{html.escape(color)}" data-series="{data}">
        <svg viewBox="0 0 1040 330" role="img" aria-label="{safe_package} weekly downloads line chart"></svg>
        <div class="chart-tooltip" role="status"></div>
      </div>
    """


def interactive_dashboard_script() -> str:
    """Inline JS for initial chart render (dashboard_range_controls.js enhances afterwards)."""
    return """
  <script>
    (() => {
      const SVG_NS = "http://www.w3.org/2000/svg";
      const numberFormat = new Intl.NumberFormat("en-US");
      function el(name, attrs = {}, text = "") {
        const node = document.createElementNS(SVG_NS, name);
        Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
        if (text) node.textContent = text;
        return node;
      }
      function compactInt(value) {
        if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
        if (value >= 1000) return `${Math.round(value / 1000)}K`;
        return `${Math.round(value)}`;
      }
      function niceYMax(maxValue) {
        if (maxValue <= 0) return 1;
        const exponent = Math.floor(Math.log10(maxValue));
        const base = 10 ** exponent;
        for (const multiplier of [1, 2, 5, 10]) {
          if (multiplier * base >= maxValue) return multiplier * base;
        }
        return 10 * base;
      }
      function filteredRows(rows, startInput, endInput) {
        const start = startInput.value;
        const end = endInput.value;
        return rows.filter((row) => (!start || row.week >= start) && (!end || row.week <= end));
      }
      function svgPoint(svg, event) {
        const point = svg.createSVGPoint();
        point.x = event.clientX;
        point.y = event.clientY;
        return point.matrixTransform(svg.getScreenCTM().inverse());
      }
      function showTooltip(wrap, event, row) {
        const tooltip = wrap.querySelector(".chart-tooltip");
        const rect = wrap.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        tooltip.innerHTML = `<strong>${row.week}</strong><span>${numberFormat.format(row.downloads)} downloads</span>`;
        tooltip.style.left = `${Math.min(Math.max(12, x + 14), rect.width - 170)}px`;
        tooltip.style.top = `${Math.max(12, y - 44)}px`;
        tooltip.classList.add("is-visible");
      }
      function hideHover(wrap, hoverGuide, hoverPoint) {
        wrap.querySelector(".chart-tooltip").classList.remove("is-visible");
        hoverGuide.setAttribute("display", "none");
        hoverPoint.setAttribute("display", "none");
      }
      function renderChart(wrap) {
        const card = wrap.closest(".chart-card");
        const startInput = card.querySelector(".range-start");
        const endInput = card.querySelector(".range-end");
        const svg = wrap.querySelector("svg");
        const color = wrap.dataset.color;
        const packageName = wrap.dataset.package;
        const allRows = JSON.parse(wrap.dataset.series || "[]");
        const rows = filteredRows(allRows, startInput, endInput);
        const width = 1040, height = 330, left = 72, right = 28, top = 34, bottom = 56;
        const plotW = width - left - right, plotH = height - top - bottom;
        svg.textContent = "";
        svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
        svg.setAttribute("aria-label", `${packageName} weekly downloads line chart`);
        svg.appendChild(el("rect", { width, height, rx: 8, fill: "#ffffff" }));
        if (!rows.length) {
          svg.appendChild(el("text", { x: width / 2, y: height / 2 - 10, "text-anchor": "middle", class: "empty-title" }, "No npm data"));
          svg.appendChild(el("text", { x: width / 2, y: height / 2 + 18, "text-anchor": "middle", class: "empty-subtitle" }, "No complete-week data in this range."));
          wrap.querySelector(".chart-tooltip").classList.remove("is-visible");
          return;
        }
        const yMax = niceYMax(Math.max(...rows.map((row) => row.downloads)));
        const xAt = (index) => rows.length === 1 ? left + plotW / 2 : left + (index / (rows.length - 1)) * plotW;
        const yAt = (value) => top + plotH - (value / yMax) * plotH;
        for (let tick = 0; tick < 5; tick += 1) {
          const value = Math.round(yMax * tick / 4);
          const y = yAt(value);
          svg.appendChild(el("line", { x1: left, x2: left + plotW, y1: y.toFixed(1), y2: y.toFixed(1), class: "grid" }));
          svg.appendChild(el("text", { x: left - 12, y: (y + 4).toFixed(1), "text-anchor": "end", class: "axis-label" }, compactInt(value)));
        }
        const tickIndexes = new Set([0, rows.length - 1]);
        for (let i = 0; i < 6; i += 1) tickIndexes.add(Math.round(i * (rows.length - 1) / 5));
        [...tickIndexes].sort((a, b) => a - b).forEach((index) => {
          const x = xAt(index);
          svg.appendChild(el("line", { x1: x.toFixed(1), x2: x.toFixed(1), y1: top + plotH, y2: top + plotH + 5, class: "tick" }));
          svg.appendChild(el("text", { x: x.toFixed(1), y: top + plotH + 26, "text-anchor": "middle", class: "axis-label" }, rows[index].week));
        });
        svg.appendChild(el("line", { x1: left, x2: left + plotW, y1: top + plotH, y2: top + plotH, class: "axis" }));
        svg.appendChild(el("line", { x1: left, x2: left, y1: top, y2: top + plotH, class: "axis" }));
        const points = rows.map((row, index) => `${xAt(index).toFixed(1)},${yAt(row.downloads).toFixed(1)}`).join(" ");
        svg.appendChild(el("polyline", { points, fill: "none", stroke: color, "stroke-width": 2.6, "stroke-linejoin": "round", "stroke-linecap": "round" }));
        const latest = rows[rows.length - 1];
        const peak = rows.reduce((best, row) => row.downloads > best.downloads ? row : best, rows[0]);
        svg.appendChild(el("text", { x: left, y: 20, class: "chart-caption" }, `Weekly downloads, ${rows[0].week} to ${latest.week}`));
        svg.appendChild(el("text", { x: left + plotW, y: 20, "text-anchor": "end", class: "chart-caption" }, `Latest: ${latest.week} / ${numberFormat.format(latest.downloads)} | Peak: ${peak.week} / ${numberFormat.format(peak.downloads)}`));
        const hoverGuide = el("line", { x1: left, x2: left, y1: top, y2: top + plotH, class: "hover-guide", display: "none" });
        const hoverPoint = el("circle", { cx: left, cy: top + plotH, r: 5, fill: "#ffffff", stroke: color, "stroke-width": 2.4, class: "hover-point", display: "none" });
        svg.appendChild(hoverGuide);
        svg.appendChild(hoverPoint);
        const overlay = el("rect", { x: left, y: top, width: plotW, height: plotH, fill: "transparent", class: "hover-overlay" });
        overlay.addEventListener("pointermove", (event) => {
          const local = svgPoint(svg, event);
          const rawIndex = rows.length === 1 ? 0 : Math.round(((local.x - left) / plotW) * (rows.length - 1));
          const index = Math.max(0, Math.min(rows.length - 1, rawIndex));
          const row = rows[index];
          const cx = xAt(index), cy = yAt(row.downloads);
          hoverGuide.setAttribute("x1", cx.toFixed(1));
          hoverGuide.setAttribute("x2", cx.toFixed(1));
          hoverGuide.removeAttribute("display");
          hoverPoint.setAttribute("cx", cx.toFixed(1));
          hoverPoint.setAttribute("cy", cy.toFixed(1));
          hoverPoint.removeAttribute("display");
          showTooltip(wrap, event, row);
        });
        overlay.addEventListener("pointerleave", () => hideHover(wrap, hoverGuide, hoverPoint));
        svg.appendChild(overlay);
      }
      document.querySelectorAll("[data-chart]").forEach((wrap) => {
        const card = wrap.closest(".chart-card");
        const startInput = card.querySelector(".range-start");
        const endInput = card.querySelector(".range-end");
        startInput.addEventListener("change", () => renderChart(wrap));
        endInput.addEventListener("change", () => renderChart(wrap));
        renderChart(wrap);
      });
    })();
  </script>
"""


# ── HTML generation ────────────────────────────────────────────────────────

def build_html(rows: list[dict[str, str]], metas: dict[str, PackageMeta], latest_day: date, config: VendorConfig) -> str:
    complete_through = latest_complete_week_start(latest_day)
    chart_last_week = complete_through.isoformat()
    chart_packages = config.chart_series or config.packages
    dashboard_script = interactive_dashboard_script()

    def render_card(package: str, index: int) -> str:
        series = series_for_package(rows, package, complete_through=complete_through)
        total = sum(value for _, value in series) if series else None
        latest = series[-1][1] if series else None
        peak = max(series, key=lambda item: item[1]) if series else None
        meta = metas.get(package)
        created = meta.created.isoformat() if meta and meta.created else "-"
        peak_label = f"{peak[0]} / {format_int(peak[1])}" if peak else "-"
        color = get_color(config, package, index)
        chart = interactive_chart_shell(package, series, color)
        desc = config.package_descriptions.get(package) or (meta.description if meta else None) or (meta.error if meta else None) or "-"
        note = config.package_notes.get(package, "")
        lv_cell = ""
        if config.include_latest_version:
            lv = html.escape(meta.latest_version or "-") if meta else "-"
            lv_cell = f'<div><dt>Latest</dt><dd>{lv}</dd></div>'
        return f"""
            <section class="chart-card">
              <div class="card-head">
                <div>
                  <h2>{html.escape(package)}</h2>
                  <p>{html.escape(desc)}</p>
                </div>
                <dl class="metrics">
                  <div><dt>Created</dt><dd>{created}</dd></div>
                  <div><dt>Chart total</dt><dd>{format_int(total)}</dd></div>
                  <div><dt>Latest complete week</dt><dd>{format_int(latest)}</dd></div>
                  <div><dt>Peak week</dt><dd>{html.escape(peak_label)}</dd></div>
                  {lv_cell}
                </dl>
              </div>
              {chart}
              <p class="note">{html.escape(note)}</p>
            </section>
            """

    if config.section_groups:
        parts = []
        pkg_to_idx = {p: i for i, p in enumerate(chart_packages)}
        for section in config.section_groups:
            parts.append(
                f'<section class="section-divider" aria-label="{html.escape(section.title.lower())}">\n'
                f'  <h2>{html.escape(section.title)}</h2>\n'
                f'  <p>{html.escape(section.subtitle)}</p>\n</section>'
            )
            for pkg in section.packages:
                parts.append(render_card(pkg, pkg_to_idx.get(pkg, 0)))
        cards_html = "\n".join(parts)
    else:
        cards_html = "\n".join(render_card(pkg, i) for i, pkg in enumerate(chart_packages))

    table_rows = []
    for package in config.packages:
        meta = metas[package]
        desc = config.package_descriptions.get(package) or meta.description or meta.error or "-"
        lv_cell = f'<td>{html.escape(meta.latest_version or "-")}</td>' if config.include_latest_version else ""
        table_rows.append(
            f'<tr><td><code>{html.escape(package)}</code></td>'
            f'<td>{"Yes" if meta.exists else "No"}</td>'
            f'<td>{html.escape(meta.created_raw or "-")}</td>'
            f'<td>{html.escape(meta.modified_raw or "-")}</td>'
            f'{lv_cell}'
            f'<td>{html.escape(desc)}</td></tr>'
        )
    lv_header = "<th>Latest</th>" if config.include_latest_version else ""

    first_week = rows[0]["week_start"] if rows else "-"
    last_week = rows[-1]["week_start"] if rows else "-"
    source_note = (
        f"CSV keeps the latest incomplete week; charts show complete weeks through {chart_last_week}. "
        "npm download counts are tarball downloads and can include CI, mirrors, bots, cache effects, and dependency installs."
    )

    return f"""<!doctype html>
<html lang="{config.lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(config.display_name)} npm Weekly Downloads Dashboard</title>
  <style>
    :root {{
      --ink: #162033; --muted: #596579; --line: #dbe2ea; --soft: #f5f7fb;
      --panel: #ffffff; --accent: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f7f8fb; color: var(--ink); }}
    main {{ width: min(1180px, calc(100vw - 32px)); margin: 0 auto; padding: 32px 0 48px; }}
    header {{ margin-bottom: 22px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; line-height: 1.2; }}
    .subtitle {{ margin: 0; color: var(--muted); font-size: 14px; line-height: 1.6; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 20px 0 24px; }}
    .summary div, .source-box {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; }}
    .summary span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .summary strong {{ font-size: 18px; font-weight: 700; }}
    .section-divider {{ margin: 28px 0 16px; padding: 18px 0 4px; border-top: 2px solid #cbd5e1; }}
    .section-divider h2 {{ margin: 0 0 4px; font-size: 22px; }}
    .section-divider p {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .chart-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    .card-head {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 18px; align-items: start; margin-bottom: 10px; }}
    h2 {{ margin: 0 0 4px; font-size: 20px; }}
    .card-head p {{ margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(86px, auto)); gap: 8px; margin: 0; }}
    .metrics div {{ border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; background: #fbfcfe; }}
    dt {{ color: var(--muted); font-size: 11px; margin-bottom: 3px; }}
    dd {{ margin: 0; font-size: 13px; font-weight: 700; white-space: nowrap; }}
    .chart-toolbar {{ display: flex; justify-content: flex-end; align-items: center; gap: 10px; flex-wrap: wrap; margin: 10px 0 8px; }}
    .chart-toolbar label {{ display: inline-flex; align-items: center; gap: 8px; color: var(--muted); font-size: 12px; }}
    .chart-toolbar input {{ color: var(--ink); border: 1px solid var(--line); border-radius: 6px; background: #ffffff; padding: 6px 9px; }}
    .chart-wrap {{ width: 100%; overflow-x: auto; position: relative; border-radius: 8px; }}
    svg {{ width: 100%; min-width: 780px; height: auto; display: block; }}
    .grid {{ stroke: #e8edf4; stroke-width: 1; }}
    .axis, .tick {{ stroke: #c8d1dc; stroke-width: 1; }}
    .axis-label {{ fill: #667085; font-size: 11px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    .chart-caption {{ fill: #475467; font-size: 12px; font-weight: 650; }}
    .hover-guide {{ stroke: #94a3b8; stroke-width: 1.2; stroke-dasharray: 4 4; pointer-events: none; }}
    .hover-overlay {{ cursor: crosshair; }}
    .empty-title {{ fill: #334155; font-size: 18px; font-weight: 700; }}
    .empty-subtitle {{ fill: #667085; font-size: 14px; }}
    .chart-tooltip {{ position: absolute; z-index: 5; min-width: 150px; opacity: 0; pointer-events: none; transform: translateY(4px); transition: opacity 120ms ease, transform 120ms ease; border: 1px solid #d0d7e2; border-radius: 8px; background: rgba(255,255,255,0.96); box-shadow: 0 10px 26px rgba(15, 23, 42, 0.12); padding: 8px 10px; }}
    .chart-tooltip.is-visible {{ opacity: 1; transform: translateY(0); }}
    .chart-tooltip strong {{ display: block; font-size: 12px; margin-bottom: 3px; }}
    .chart-tooltip span {{ display: block; color: var(--muted); font-size: 12px; }}
    .note {{ margin: 12px 0 0; color: #334155; font-size: 14px; line-height: 1.65; background: var(--soft); border-left: 3px solid var(--accent); padding: 10px 12px; }}
    .source-box {{ margin-top: 18px; }}
    .source-box h2 {{ margin-bottom: 10px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-top: 1px solid var(--line); padding: 9px 8px; text-align: left; vertical-align: top; }}
    th {{ color: #475467; font-weight: 700; background: #fbfcfe; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
    @media (max-width: 860px) {{
      main {{ width: min(100vw - 20px, 1180px); padding-top: 20px; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .card-head {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      h1 {{ font-size: 24px; }}
    }}
  </style>
  <link rel="stylesheet" href="../dashboard_range_controls.css">
</head>
<body>
  <main>
    <header>
      <h1>{html.escape(config.display_name)} npm Weekly Downloads Dashboard</h1>
      <p class="subtitle">Data from npm official downloads API, aggregated by Monday-start weeks. CSV retains the latest incomplete week; HTML charts show complete weeks only. npm download counts include CI, mirrors, bots, cache effects, and dependency installs.</p>
    </header>
    <section class="summary" aria-label="dashboard summary">
      <div><span>CSV rows</span><strong>{len(rows)}</strong></div>
      <div><span>Week range</span><strong>{first_week} to {last_week}</strong></div>
      <div><span>Chart through</span><strong>{chart_last_week}</strong></div>
      <div><span>Latest npm day</span><strong>{latest_day.isoformat()}</strong></div>
    </section>
    {cards_html}
    <section class="source-box">
      <h2>Source And Package Metadata</h2>
      <table>
        <thead><tr><th>Package</th><th>Found</th><th>Created</th><th>Modified</th>{lv_header}<th>Description / Error</th></tr></thead>
        <tbody>{''.join(table_rows)}</tbody>
      </table>
      <p class="subtitle">Output CSV: <code>{html.escape(config.csv_path.name)}</code>. Metadata JSON: <code>{html.escape(config.meta_path.name)}</code>. {html.escape(source_note)}</p>
    </section>
  </main>
  {dashboard_script}
  <script src="../dashboard_range_controls.js"></script>
</body>
</html>"""


# ── Metadata JSON ──────────────────────────────────────────────────────────

def write_metadata(metas: dict[str, PackageMeta], rows: list[dict[str, str]], latest_day: date, config: VendorConfig) -> None:
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "vendor": config.vendor,
        "source": {
            "registry": NPM_REGISTRY,
            "downloads": NPM_DOWNLOADS,
            "range_limit_note": f"npm downloads API is queried in {MAX_RANGE_DAYS}-day chunks.",
            "weekly_grain": "Monday-start weeks",
            "latest_download_day": latest_day.isoformat(),
            "html_chart_complete_through_week_start": latest_complete_week_start(latest_day).isoformat(),
            "html_chart_policy": "HTML line charts exclude the latest incomplete week; CSV retains all weekly aggregates.",
            "caveat": "npm download counts include automation, mirrors, robots, cache effects, and dependency installs.",
        },
        "csv": {
            "path": str(config.csv_path),
            "rows": len(rows),
            "columns": get_csv_columns(config),
        },
        "packages": {
            name: {
                "exists": meta.exists,
                "created": meta.created_raw,
                "modified": meta.modified_raw,
                "latest_version": meta.latest_version,
                "description": meta.description,
                "error": meta.error,
            }
            for name, meta in metas.items()
        },
    }
    if config.derived_columns:
        metadata["derived_columns"] = {
            name: {"formula": f"sum({'+'.join(sources)})", "sources": sources}
            for name, sources in config.derived_columns.items()
        }
    config.meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Entry point ────────────────────────────────────────────────────────────

def run(config: VendorConfig) -> dict:
    """Run the full dashboard update pipeline for a single vendor."""
    metas = {p: load_package_meta(p, user_agent=config.user_agent) for p in config.packages}
    latest_day = latest_download_day()
    weekly_data: dict[str, dict[date, int]] = {}
    for package, meta in metas.items():
        if not meta.exists or meta.created is None:
            weekly_data[package] = {}
            continue
        start = max(meta.created, EARLIEST_NPM_DOWNLOAD_DATE)
        daily = load_daily_downloads(package, start, latest_day, user_agent=config.user_agent)
        weekly_data[package] = weekly_from_daily(daily)
    rows = build_csv_rows(metas, weekly_data, latest_day, config)
    columns = get_csv_columns(config)
    write_csv(rows, config.csv_path, columns)
    config.html_path.write_text(build_html(rows, metas, latest_day, config), encoding="utf-8")
    write_metadata(metas, rows, latest_day, config)
    return {
        "csv": str(config.csv_path),
        "html": str(config.html_path),
        "metadata": str(config.meta_path),
        "rows": len(rows),
        "latest_download_day": latest_day.isoformat(),
        "packages": {n: {"exists": m.exists, "created": m.created_raw} for n, m in metas.items()},
    }


def run_from_existing(config: VendorConfig) -> dict:
    """Rebuild HTML and metadata from existing CSV + metadata JSON (no network calls)."""
    import csv as _csv
    rows: list[dict[str, str]] = []
    with config.csv_path.open(newline="", encoding="utf-8") as handle:
        reader = _csv.DictReader(handle)
        for row in reader:
            rows.append(dict(row))
    meta_json = json.loads(config.meta_path.read_text(encoding="utf-8"))
    metas: dict[str, PackageMeta] = {}
    for package in config.packages:
        pm = meta_json.get("packages", {}).get(package, {})
        metas[package] = PackageMeta(
            name=package,
            exists=pm.get("exists", False),
            created_raw=pm.get("created"),
            modified_raw=pm.get("modified"),
            description=pm.get("description"),
            latest_version=pm.get("latest_version"),
            error=pm.get("error"),
        )
        if pm.get("created"):
            try:
                metas[package].created = parse_iso_date(pm["created"])
            except Exception:  # noqa: BLE001
                pass
    latest_day_str = meta_json.get("source", {}).get("latest_download_day") or (rows[-1]["week_start"] if rows else latest_download_day().isoformat())
    latest_day = parse_iso_date(latest_day_str) if "T" in latest_day_str else date.fromisoformat(latest_day_str)
    config.html_path.write_text(build_html(rows, metas, latest_day, config), encoding="utf-8")
    write_metadata(metas, rows, latest_day, config)
    return {"csv": str(config.csv_path), "html": str(config.html_path), "metadata": str(config.meta_path), "rows": len(rows)}

