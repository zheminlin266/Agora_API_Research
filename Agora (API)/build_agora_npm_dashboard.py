from __future__ import annotations

import csv
import html
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


CORE_PACKAGES = [
    "agora-rtc-sdk-ng",
    "agora-rtc-sdk",
    "agora-rtm-sdk",
    "agora-rtc-react",
    "react-native-agora",
]
AI_PACKAGES = [
    "agora-agent-server-sdk",
    "agora-agent-client-toolkit",
    "agora-agent-uikit",
    "agora-conversational-ai-denoiser",
]
PACKAGES = [*CORE_PACKAGES, *AI_PACKAGES]
DERIVED_COLUMNS = ["rtc-sdk-total"]
CSV_COLUMNS = [
    "week_start",
    "agora-rtc-sdk-ng",
    "agora-rtc-sdk",
    "rtc-sdk-total",
    "agora-rtm-sdk",
    "agora-rtc-react",
    "react-native-agora",
    *AI_PACKAGES,
]
CORE_CHART_SERIES = [
    "agora-rtc-sdk-ng",
    "agora-rtc-sdk",
    "rtc-sdk-total",
    "agora-rtm-sdk",
    "agora-rtc-react",
    "react-native-agora",
]
AI_CHART_SERIES = [*AI_PACKAGES]

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "agora_npm_weekly_downloads.csv"
HTML_PATH = ROOT / "agora_npm_downloads_dashboard.html"
META_PATH = ROOT / "agora_npm_downloads_metadata.json"

NPM_REGISTRY = "https://registry.npmjs.org"
NPM_DOWNLOADS = "https://api.npmjs.org/downloads"
EARLIEST_NPM_DOWNLOAD_DATE = date(2015, 1, 10)
MAX_RANGE_DAYS = 548


@dataclass
class PackageMeta:
    name: str
    exists: bool
    created: date | None = None
    created_raw: str | None = None
    modified_raw: str | None = None
    description: str | None = None
    error: str | None = None


def fetch_json(url: str, retries: int = 6) -> dict:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "codex-agora-npm-weekly-dashboard/1.0",
                },
            )
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries - 1:
                retry_after = exc.headers.get("Retry-After")
                try:
                    wait_seconds = float(retry_after) if retry_after else 30 * (attempt + 1)
                except ValueError:
                    wait_seconds = 30 * (attempt + 1)
                time.sleep(wait_seconds)
                continue
            raise
        except Exception as exc:  # noqa: BLE001 - keep network retry compact.
            last_error = exc
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def url_package(package: str) -> str:
    return urllib.parse.quote(package, safe="")


def parse_iso_date(raw: str) -> date:
    normalized = raw.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc).date()


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
    base = 10**exponent
    for multiplier in (1, 2, 5, 10):
        candidate = multiplier * base
        if candidate >= max_value:
            return int(candidate)
    return int(10 * base)


def load_package_meta(package: str) -> PackageMeta:
    try:
        data = fetch_json(f"{NPM_REGISTRY}/{url_package(package)}")
    except urllib.error.HTTPError as exc:
        return PackageMeta(name=package, exists=False, error=f"HTTP {exc.code}: {exc.reason}")

    created_raw = data.get("time", {}).get("created")
    created = parse_iso_date(created_raw) if created_raw else None
    return PackageMeta(
        name=package,
        exists=True,
        created=created,
        created_raw=created_raw,
        modified_raw=data.get("time", {}).get("modified"),
        description=data.get("description") or "",
    )


def latest_download_day() -> date:
    data = fetch_json(f"{NPM_DOWNLOADS}/point/last-day")
    return date.fromisoformat(data["end"])


def load_daily_downloads(package: str, start: date, end: date) -> dict[date, int]:
    daily: dict[date, int] = {}
    for chunk_start, chunk_end in iter_ranges(start, end):
        period = f"{chunk_start.isoformat()}:{chunk_end.isoformat()}"
        url = f"{NPM_DOWNLOADS}/range/{period}/{url_package(package)}"
        try:
            payload = fetch_json(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise
        time.sleep(0.35)
        for row in payload.get("downloads", []):
            daily[date.fromisoformat(row["day"])] = int(row.get("downloads", 0))
    return daily


def weekly_from_daily(daily: dict[date, int]) -> dict[date, int]:
    weekly: dict[date, int] = {}
    for day, downloads in daily.items():
        start = week_start(day)
        weekly[start] = weekly.get(start, 0) + downloads
    return weekly


def build_csv_rows(
    metas: dict[str, PackageMeta],
    weekly_data: dict[str, dict[date, int]],
    latest_day: date,
) -> list[dict[str, str]]:
    existing_starts = [
        week_start(meta.created)
        for meta in metas.values()
        if meta.exists and meta.created is not None
    ]
    if not existing_starts:
        return []

    first_week = min(existing_starts)
    last_week = week_start(latest_day)
    package_start_weeks = {
        name: week_start(meta.created) if meta.created else None
        for name, meta in metas.items()
    }

    rows: list[dict[str, str]] = []
    current = first_week
    while current <= last_week:
        row: dict[str, str] = {"week_start": current.isoformat()}
        for package in PACKAGES:
            meta = metas[package]
            start_week = package_start_weeks.get(package)
            if not meta.exists or start_week is None or current < start_week:
                row[package] = ""
            else:
                row[package] = str(weekly_data.get(package, {}).get(current, 0))
        rtc_values = [row["agora-rtc-sdk-ng"], row["agora-rtc-sdk"]]
        row["rtc-sdk-total"] = (
            str(sum(int(value) for value in rtc_values if value != ""))
            if any(value != "" for value in rtc_values)
            else ""
        )
        rows.append(row)
        current += timedelta(days=7)
    return rows


def write_csv(rows: list[dict[str, str]]) -> None:
    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def latest_complete_week_start(latest_day: date) -> date:
    current_week = week_start(latest_day)
    if latest_day >= current_week + timedelta(days=6):
        return current_week
    return current_week - timedelta(days=7)


def series_for_package(
    rows: list[dict[str, str]],
    package: str,
    complete_through: date | None = None,
) -> list[tuple[str, int]]:
    series = []
    for row in rows:
        row_week = date.fromisoformat(row["week_start"])
        if complete_through is not None and row_week > complete_through:
            continue
        value = row.get(package, "")
        if value != "":
            series.append((row["week_start"], int(value)))
    return series


def svg_line_chart(package: str, series: list[tuple[str, int]], color: str) -> str:
    width = 1040
    height = 330
    left = 72
    right = 28
    top = 34
    bottom = 56
    plot_w = width - left - right
    plot_h = height - top - bottom

    if not series:
        return f"""
        <svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(package)} no data">
          <rect width="{width}" height="{height}" rx="8" fill="#ffffff"/>
          <text x="{width / 2}" y="{height / 2 - 10}" text-anchor="middle" class="empty-title">No npm data</text>
          <text x="{width / 2}" y="{height / 2 + 18}" text-anchor="middle" class="empty-subtitle">Exact package name was not found in npm registry.</text>
        </svg>
        """

    max_value = max(value for _, value in series)
    y_max = nice_y_max(max_value)

    def x_at(index: int) -> float:
        if len(series) == 1:
            return left + plot_w / 2
        return left + (index / (len(series) - 1)) * plot_w

    def y_at(value: int) -> float:
        return top + plot_h - (value / y_max) * plot_h

    points = " ".join(
        f"{x_at(index):.1f},{y_at(value):.1f}" for index, (_, value) in enumerate(series)
    )
    area_points = f"{left},{top + plot_h} {points} {left + plot_w},{top + plot_h}"

    y_ticks = []
    for tick in range(5):
        value = round(y_max * tick / 4)
        y = y_at(value)
        y_ticks.append(
            f'<line x1="{left}" x2="{left + plot_w}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>'
            f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" class="axis-label">{compact_int(value)}</text>'
        )

    tick_indexes = sorted({0, len(series) - 1, *(round(i * (len(series) - 1) / 5) for i in range(6))})
    x_ticks = []
    for index in tick_indexes:
        label = series[index][0]
        x = x_at(index)
        x_ticks.append(
            f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top + plot_h}" y2="{top + plot_h + 5}" class="tick"/>'
            f'<text x="{x:.1f}" y="{top + plot_h + 26}" text-anchor="middle" class="axis-label">{label}</text>'
        )

    latest_label, latest_value = series[-1]
    peak_label, peak_value = max(series, key=lambda item: item[1])
    latest_x = x_at(len(series) - 1)
    latest_y = y_at(latest_value)

    return f"""
    <svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(package)} weekly downloads line chart">
      <defs>
        <linearGradient id="fill-{html.escape(package)}" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="{color}" stop-opacity="0.20"/>
          <stop offset="100%" stop-color="{color}" stop-opacity="0.03"/>
        </linearGradient>
      </defs>
      <rect width="{width}" height="{height}" rx="8" fill="#ffffff"/>
      {''.join(y_ticks)}
      <line x1="{left}" x2="{left + plot_w}" y1="{top + plot_h}" y2="{top + plot_h}" class="axis"/>
      <line x1="{left}" x2="{left}" y1="{top}" y2="{top + plot_h}" class="axis"/>
      {''.join(x_ticks)}
      <polygon points="{area_points}" fill="url(#fill-{html.escape(package)})"/>
      <polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>
      <circle cx="{latest_x:.1f}" cy="{latest_y:.1f}" r="4.2" fill="#ffffff" stroke="{color}" stroke-width="2.4"/>
      <text x="{left}" y="20" class="chart-caption">Weekly downloads, Monday-start weeks</text>
      <text x="{left + plot_w}" y="20" text-anchor="end" class="chart-caption">Latest: {latest_label} / {format_int(latest_value)} · Peak: {peak_label} / {format_int(peak_value)}</text>
    </svg>
    """


def package_note(package: str) -> str:
    notes = {
        "agora-rtc-sdk-ng": (
            "功能：Agora WebRTC JavaScript 核心 SDK。它更接近 Web 端音视频通话、直播互动、在线课堂等实际集成需求。下载数包含 CI、镜像和重复安装，不能等同客户数或用量；看趋势、峰值和版本发布后的变化，比看绝对值更可靠。"
        ),
        "agora-rtc-sdk": (
            "功能：Agora 旧版 Web RTC JavaScript SDK。它反映 legacy Web 集成、历史项目维护或旧版本依赖需求。数值应与 agora-rtc-sdk-ng 分开看，不能直接相加；若旧包下降而 NG 包上升，通常意味着迁移到新版 SDK。"
        ),
        "rtc-sdk-total": (
            "功能：agora-rtc-sdk-ng 与 agora-rtc-sdk 的周度下载合计。它用于观察 Agora Web RTC SDK 总体开发者安装需求，减少新旧包迁移造成的误读；但仍包含 CI、镜像和重复安装，不能代表真实客户数或用量。"
        ),
        "agora-rtm-sdk": (
            "功能：Agora Real-Time Messaging 的 JavaScript SDK。它反映实时消息、信令、在线状态、房间控制等互动能力需求。数值可作为 JS 侧 RTM 采用热度，但可能被依赖安装和自动构建放大，适合与 RTC 包趋势交叉判断。"
        ),
        "agora-rtc-react": (
            "功能：Agora RTC 的 React 封装。它揭示 React 开发者希望用组件化方式接入实时音视频的需求，更多是前端框架生态信号。它通常会与 Web RTC 核心包重叠，不能简单与 agora-rtc-sdk-ng 相加。"
        ),
        "react-native-agora": (
            "功能：Agora RTC 的 React Native SDK。它反映跨平台移动端应用接入语音、视频通话和互动直播的开发需求。下载数包含 CI、镜像和依赖安装，不能等同移动端活跃应用数；更适合观察移动开发者采用趋势。"
        ),
        "agora-agent-server-sdk": (
            "功能：Agora Agent 服务端 SDK/兼容包，面向实时语音 Agent、会话控制和服务端集成。它反映开发者在后端接入 Agora Conversational AI/Agent 能力的需求；下载量较小，适合看早期采用趋势。"
        ),
        "agora-agent-client-toolkit": (
            "功能：Agora Agent 客户端工具包，用于在前端接入实时语音 Agent、会话状态和交互控制。它反映开发者把 AI Agent 体验嵌入 Web 或应用端的需求，下载量可作为客户端 Agent 集成热度信号。"
        ),
        "agora-agent-uikit": (
            "功能：Agora Agent UI Kit，提供构建语音、视频或对话式 AI Agent 界面的组件。它反映开发者希望用现成 UI 快速集成 AI Agent 体验的需求；数值更偏产品化前端组件采用。"
        ),
        "agora-conversational-ai-denoiser": (
            "功能：Agora Conversational AI 场景的 Web SDK 降噪扩展。它反映语音 Agent、对话 AI 和实时互动中对语音清晰度、噪声抑制的需求，适合观察 AI 语音体验优化相关采用。"
        ),
    }
    return notes[package]


def build_html(rows: list[dict[str, str]], metas: dict[str, PackageMeta], latest_day: date) -> str:
    complete_through = latest_complete_week_start(latest_day)
    colors = {
        "agora-rtc-sdk-ng": "#2563eb",
        "agora-rtc-sdk": "#d97706",
        "rtc-sdk-total": "#be123c",
        "agora-rtm-sdk": "#b7791f",
        "agora-rtc-react": "#0f766e",
        "react-native-agora": "#7c3aed",
        "agora-agent-server-sdk": "#475569",
        "agora-agent-client-toolkit": "#0891b2",
        "agora-agent-uikit": "#db2777",
        "agora-conversational-ai-denoiser": "#65a30d",
    }

    def render_card(package: str) -> str:
        series = series_for_package(rows, package, complete_through=complete_through)
        total = sum(value for _, value in series) if series else None
        latest = series[-1][1] if series else None
        non_zero = sum(1 for _, value in series if value > 0)
        meta = metas.get(package)
        status = "Derived" if meta is None else ("Found" if meta.exists else "Not found")
        created = "-" if meta is None else (meta.created_raw[:10] if meta.created_raw else "-")
        description = (
            "Derived sum of agora-rtc-sdk-ng and agora-rtc-sdk."
            if meta is None
            else (meta.description or meta.error or "No npm registry record.")
        )
        chart = svg_line_chart(package, series, colors[package])
        return f"""
            <section class="chart-card">
              <div class="card-head">
                <div>
                  <h2>{html.escape(package)}</h2>
                  <p>{html.escape(description)}</p>
                </div>
                <dl class="metrics">
                  <div><dt>Status</dt><dd>{status}</dd></div>
                  <div><dt>Created</dt><dd>{created}</dd></div>
                  <div><dt>Chart total</dt><dd>{format_int(total)}</dd></div>
                  <div><dt>Latest complete week</dt><dd>{format_int(latest)}</dd></div>
                  <div><dt>Non-zero weeks</dt><dd>{format_int(non_zero)}</dd></div>
                </dl>
              </div>
              <div class="chart-wrap">{chart}</div>
              <p class="note">{html.escape(package_note(package))}</p>
            </section>
            """

    core_cards = [render_card(package) for package in CORE_CHART_SERIES]
    ai_cards = [render_card(package) for package in AI_CHART_SERIES]

    package_rows = []
    for package in PACKAGES:
        meta = metas[package]
        package_rows.append(
            f"""
            <tr>
              <td>{html.escape(package)}</td>
              <td>{'yes' if meta.exists else 'no'}</td>
              <td>{html.escape(meta.created_raw or '-')}</td>
              <td>{html.escape(meta.modified_raw or '-')}</td>
              <td>{html.escape(meta.description or meta.error or '')}</td>
            </tr>
            """
        )

    first_week = rows[0]["week_start"] if rows else "-"
    last_week = rows[-1]["week_start"] if rows else "-"
    row_count = len(rows)
    chart_last_week = complete_through.isoformat()

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agora npm Weekly Downloads Dashboard</title>
  <style>
    :root {{
      --ink: #162033;
      --muted: #596579;
      --line: #dbe2ea;
      --soft: #f5f7fb;
      --panel: #ffffff;
      --accent: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f8fb;
      color: var(--ink);
    }}
    main {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 32px 0 48px;
    }}
    header {{
      margin-bottom: 22px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 20px 0 24px;
    }}
    .summary div, .source-box {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
    }}
    .summary span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .summary strong {{
      font-size: 18px;
      font-weight: 700;
    }}
    .chart-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 18px;
    }}
    .section-divider {{
      margin: 28px 0 16px;
      padding: 18px 0 4px;
      border-top: 2px solid #cbd5e1;
    }}
    .section-divider h2 {{
      margin: 0 0 4px;
      font-size: 22px;
    }}
    .section-divider p {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    .card-head {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 18px;
      align-items: start;
      margin-bottom: 10px;
    }}
    h2 {{
      margin: 0 0 4px;
      font-size: 20px;
      line-height: 1.25;
      letter-spacing: 0;
    }}
    .card-head p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(5, minmax(86px, auto));
      gap: 8px;
      margin: 0;
    }}
    .metrics div {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px 10px;
      background: #fbfcfe;
    }}
    dt {{
      color: var(--muted);
      font-size: 11px;
      margin-bottom: 3px;
    }}
    dd {{
      margin: 0;
      font-size: 13px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .chart-wrap {{
      width: 100%;
      overflow-x: auto;
    }}
    svg {{
      width: 100%;
      min-width: 760px;
      height: auto;
      display: block;
    }}
    .grid {{
      stroke: #e7ecf2;
      stroke-width: 1;
    }}
    .axis, .tick {{
      stroke: #98a3b3;
      stroke-width: 1;
    }}
    .axis-label {{
      fill: #667085;
      font-size: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    .chart-caption {{
      fill: #475467;
      font-size: 12px;
      font-weight: 650;
    }}
    .empty-title {{
      fill: #334155;
      font-size: 24px;
      font-weight: 700;
    }}
    .empty-subtitle {{
      fill: #667085;
      font-size: 14px;
    }}
    .note {{
      margin: 12px 0 0;
      color: #334155;
      font-size: 14px;
      line-height: 1.65;
      background: var(--soft);
      border-left: 3px solid var(--accent);
      padding: 10px 12px;
    }}
    .source-box {{
      margin-top: 18px;
    }}
    .source-box h2 {{
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      border-top: 1px solid var(--line);
      padding: 9px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: #475467;
      font-weight: 700;
      background: #fbfcfe;
    }}
    code {{
      background: #eef2f7;
      padding: 2px 5px;
      border-radius: 4px;
    }}
    @media (max-width: 860px) {{
      main {{ width: min(100vw - 20px, 1180px); padding-top: 20px; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .card-head {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      h1 {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Agora npm 周度下载量看板</h1>
      <p class="subtitle">
        数据来自 npm 官方 downloads API，按周一作为每周开始日期汇总。HTML 折线图只展示完整周，已排除最新不完整周。npm 下载数是包 tarball 下载次数，会包含 CI、镜像、机器人和缓存影响，适合看趋势，不等于客户数、开发者人数或 Agora 实际用量。
      </p>
    </header>

    <section class="summary" aria-label="dashboard summary">
      <div><span>CSV rows</span><strong>{row_count}</strong></div>
      <div><span>Week range</span><strong>{first_week} to {last_week}</strong></div>
      <div><span>Chart through</span><strong>{chart_last_week}</strong></div>
      <div><span>Latest npm day</span><strong>{latest_day.isoformat()}</strong></div>
    </section>

    {''.join(core_cards)}

    <section class="section-divider" aria-label="AI related section">
      <h2>AI related</h2>
      <p>Agent, conversational AI, and AI voice enhancement packages.</p>
    </section>

    {''.join(ai_cards)}

    <section class="source-box">
      <h2>Source And Package Metadata</h2>
      <table>
        <thead>
          <tr>
            <th>Package</th>
            <th>Found</th>
            <th>Created</th>
            <th>Modified</th>
            <th>Description / Error</th>
          </tr>
        </thead>
        <tbody>{''.join(package_rows)}</tbody>
      </table>
      <p class="subtitle">
        Output CSV: <code>{html.escape(CSV_PATH.name)}</code>. Metadata JSON: <code>{html.escape(META_PATH.name)}</code>.
        CSV 保留最新不完整周；HTML 图表展示到最新完整周 <code>{chart_last_week}</code>。
      </p>
    </section>
  </main>
</body>
</html>
"""


def write_metadata(
    metas: dict[str, PackageMeta],
    rows: list[dict[str, str]],
    latest_day: date,
) -> None:
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "registry": NPM_REGISTRY,
            "downloads": NPM_DOWNLOADS,
            "range_limit_note": f"npm downloads API is queried in {MAX_RANGE_DAYS}-day chunks.",
            "weekly_grain": "Monday-start weeks",
            "latest_download_day": latest_day.isoformat(),
            "html_chart_complete_through_week_start": latest_complete_week_start(latest_day).isoformat(),
            "html_chart_policy": "HTML line charts exclude the latest incomplete week; CSV retains all weekly aggregates.",
            "caveat": "npm download counts include automation, mirrors, robots, and cache effects.",
        },
        "csv": {
            "path": str(CSV_PATH),
            "rows": len(rows),
            "columns": CSV_COLUMNS,
        },
        "derived_columns": {
            "rtc-sdk-total": {
                "formula": "agora-rtc-sdk-ng + agora-rtc-sdk",
                "blank_policy": "Blank when both source package columns are blank; otherwise blank source cells count as zero.",
            }
        },
        "packages": {
            name: {
                "exists": meta.exists,
                "created": meta.created_raw,
                "modified": meta.modified_raw,
                "description": meta.description,
                "error": meta.error,
            }
            for name, meta in metas.items()
        },
    }
    META_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    global CSV_PATH, HTML_PATH, META_PATH

    metas = {package: load_package_meta(package) for package in PACKAGES}
    latest_day = latest_download_day()
    weekly_data: dict[str, dict[date, int]] = {}

    for package, meta in metas.items():
        if not meta.exists or meta.created is None:
            weekly_data[package] = {}
            continue
        start = max(meta.created, EARLIEST_NPM_DOWNLOAD_DATE)
        daily = load_daily_downloads(package, start, latest_day)
        weekly_data[package] = weekly_from_daily(daily)

    rows = build_csv_rows(metas, weekly_data, latest_day)
    try:
        write_csv(rows)
    except PermissionError:
        CSV_PATH = ROOT / "agora_npm_weekly_downloads_updated.csv"
        HTML_PATH = ROOT / "agora_npm_downloads_dashboard_updated.html"
        META_PATH = ROOT / "agora_npm_downloads_metadata_updated.json"
        write_csv(rows)
    HTML_PATH.write_text(build_html(rows, metas, latest_day), encoding="utf-8")
    write_metadata(metas, rows, latest_day)

    print(json.dumps({
        "csv": str(CSV_PATH),
        "html": str(HTML_PATH),
        "metadata": str(META_PATH),
        "rows": len(rows),
        "latest_download_day": latest_day.isoformat(),
        "packages": {name: {"exists": meta.exists, "created": meta.created_raw} for name, meta in metas.items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
