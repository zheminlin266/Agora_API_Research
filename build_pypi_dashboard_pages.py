from __future__ import annotations

import csv
import html
import json
from dataclasses import dataclass, replace
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class PackageConfig:
    key: str
    name: str
    role: str
    color: str
    note: str
    status: str = "Found"


@dataclass(frozen=True)
class PageConfig:
    label: str
    title: str
    output: str
    csv_file: str
    source_last_date: str
    source_label: str
    source_note: str
    interpretation: str
    packages: tuple[PackageConfig, ...]


PAGES = (
    PageConfig(
        label="Agora / PyPI Weekly Downloads",
        title="Agora Python Package Download Signals",
        output="agora_pypi_weekly_downloads_dashboard.html",
        csv_file="agora_pypi_weekly_downloads.csv",
        source_last_date="2026-06-10",
        source_label="ClickPy public ClickHouse table pypi.pypi_downloads_per_day",
        source_note=(
            "PyPI 下载量是包文件被 pip、CI/CD、镜像、开发环境或自动化构建拉取的次数。"
            "它更适合观察开发者接入和后端集成需求的方向变化，不应直接等同为唯一开发者、活跃应用或付费客户。"
        ),
        interpretation=(
            "读图时重点看连续数周的趋势和包之间的相对强弱，而不是单周尖峰。"
            "token-builder 更靠近服务端鉴权接入，server-sdk 更靠近 Python 后端调用，python-sdk 带有旧包和测试/自动化噪声，"
            "realtime-ai 包体量小但能提示语音 AI / Agent 方向的早期兴趣。"
        ),
        packages=(
            PackageConfig(
                key="agora_token_builder_downloads",
                name="agora-token-builder",
                role="Token Builder",
                color="#126c73",
                note=(
                    "功能：服务端生成 Agora RTC/RTM token，用于鉴权、频道加入权限和后端接入流程。"
                    "该包的持续上行通常更接近后端项目开始集成 Agora 鉴权体系的信号。"
                ),
            ),
            PackageConfig(
                key="agora_python_server_sdk_downloads",
                name="agora-python-server-sdk",
                role="Server SDK",
                color="#a45a2a",
                note=(
                    "功能：Python 服务端 SDK，面向房间、用户、录制、REST/服务端 API 等后台管理能力。"
                    "它更能反映 Python 后端服务把 Agora 能力接入生产或测试环境的需求。"
                ),
            ),
            PackageConfig(
                key="agora_python_sdk_downloads",
                name="agora-python-sdk",
                role="Python SDK",
                color="#5661a6",
                note=(
                    "功能：较早期或通用 Python SDK 包，可能包含历史依赖、测试、自动化脚本和旧项目拉取。"
                    "该列适合看长期基线和老包残余需求，不适合单独代表新产品采用。"
                ),
            ),
            PackageConfig(
                key="agora_realtime_ai_api_v1_downloads",
                name="agora-realtime-ai-api-v1",
                role="Realtime AI",
                color="#805a7a",
                note=(
                    "功能：实时 AI / 语音 AI API 相关包，面向低延迟语音交互、Agent 或实时会话实验。"
                    "目前基数较小，重点看是否出现连续多周放量，而不是单周波动。"
                ),
            ),
        ),
    ),
    PageConfig(
        label="LiveKit / PyPI Weekly Downloads",
        title="LiveKit Python Package Download Signals",
        output="livekit_pypi_downloads_dashboard.html",
        csv_file="livekit_pypi_weekly_downloads.csv",
        source_last_date="2026-06-12",
        source_label="ClickPy public ClickHouse table pypi.pypi_downloads_per_day",
        source_note=(
            "PyPI 下载量统计包文件拉取次数，会受到 CI/CD、容器构建、依赖锁定、镜像缓存和自动化安装影响。"
            "它适合做开发者需求和生态热度的方向性指标，不能直接当作客户数、应用数或真实流量。"
        ),
        interpretation=(
            "读图时应把 livekit、livekit-api、livekit-agents 分开看：SDK、服务端 API 和 Agent 框架代表不同接入环节。"
            "三者同时上行通常说明 Python 生态的端到端集成在扩大；plugins 目前体量极小且 PyPI metadata 当前 404，应只作为低权重线索。"
        ),
        packages=(
            PackageConfig(
                key="livekit",
                name="livekit",
                role="Python SDK",
                color="#126c73",
                note=(
                    "功能：LiveKit Python realtime SDK，用于 WebRTC 音频、视频、数据通道和实时应用集成。"
                    "它是最宽口径的 Python SDK 采用信号，常同时包含本地开发、服务部署和 AI voice app 依赖拉取。"
                ),
            ),
            PackageConfig(
                key="livekit-api",
                name="livekit-api",
                role="Server API",
                color="#a45a2a",
                note=(
                    "功能：LiveKit Server API 和 token 生成包，用于房间管理、访问控制、服务端调度和后台集成。"
                    "它更贴近后端服务把 LiveKit 接入业务流程的活动。"
                ),
            ),
            PackageConfig(
                key="livekit-agents",
                name="livekit-agents",
                role="Agents",
                color="#5661a6",
                note=(
                    "功能：构建实时语音 AI Agent 的 Python 框架，连接音频流、LLM、TTS/STT、工具调用和会话控制。"
                    "该列是观察 LiveKit 在 voice AI / agent 应用方向开发者动能的关键指标。"
                ),
            ),
            PackageConfig(
                key="livekit-plugins",
                name="livekit-plugins",
                role="Plugins",
                color="#805a7a",
                status="PyPI metadata 404",
                note=(
                    "功能：插件生态相关包名在 ClickPy 下载表中有少量历史记录，但 PyPI JSON metadata 当前返回 404。"
                    "因此该列应作为异常/早期噪声看待，只有连续放量才值得进一步追踪。"
                ),
            ),
        ),
    ),
)


def read_rows(csv_file: str) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    with (ROOT / csv_file).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            out: dict[str, int | str] = {"week_start": row["week_start"]}
            for key, value in row.items():
                if key == "week_start":
                    continue
                out[key] = int(value or 0)
            rows.append(out)
    return rows


def latest_complete_week(rows: list[dict[str, int | str]], source_last_date: str) -> str:
    source_date = date.fromisoformat(source_last_date)
    complete = str(rows[-1]["week_start"])
    for row in rows:
        week = date.fromisoformat(str(row["week_start"]))
        if (source_date - week).days >= 6:
            complete = str(row["week_start"])
    return complete


def compact(value: int | float) -> str:
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}k"
    return f"{value:.0f}"


def fmt_int(value: int | float) -> str:
    return f"{int(round(value)):,}"


def pct_change(current: int | float, prior: int | float) -> str:
    if not prior:
        return "n/a"
    return f"{(current / prior - 1) * 100:+.1f}%"


def page_metrics(rows: list[dict[str, int | str]], config: PageConfig) -> dict[str, str]:
    complete_week = latest_complete_week(rows, config.source_last_date)
    complete_idx = next(i for i, row in enumerate(rows) if row["week_start"] == complete_week)
    total_all = sum(sum(int(row[pkg.key]) for pkg in config.packages) for row in rows)
    latest_total = sum(int(rows[complete_idx][pkg.key]) for pkg in config.packages)
    trailing_start = max(0, complete_idx - 11)
    prior_start = max(0, trailing_start - 12)
    trailing = sum(sum(int(row[pkg.key]) for pkg in config.packages) for row in rows[trailing_start : complete_idx + 1])
    prior = sum(sum(int(row[pkg.key]) for pkg in config.packages) for row in rows[prior_start:trailing_start])
    leader = max(config.packages, key=lambda pkg: int(rows[complete_idx][pkg.key]))
    leader_value = int(rows[complete_idx][leader.key])
    leader_share = leader_value / latest_total if latest_total else 0
    return {
        "row_count": str(len(rows)),
        "first_week": str(rows[0]["week_start"]),
        "last_week": str(rows[-1]["week_start"]),
        "complete_week": complete_week,
        "total_all": fmt_int(total_all),
        "latest_total": fmt_int(latest_total),
        "trailing_change": pct_change(trailing, prior),
        "leader": f"{leader.name} · {leader_share * 100:.1f}%",
    }


def package_cards(rows: list[dict[str, int | str]], config: PageConfig) -> str:
    cards: list[str] = []
    complete_week = latest_complete_week(rows, config.source_last_date)
    complete_idx = next(i for i, row in enumerate(rows) if row["week_start"] == complete_week)
    min_week = str(rows[0]["week_start"])
    max_week = str(rows[-1]["week_start"])
    for pkg in config.packages:
        values = [int(row[pkg.key]) for row in rows]
        chart_total = sum(values)
        latest_value = int(rows[complete_idx][pkg.key])
        peak_idx = max(range(len(rows)), key=lambda i: int(rows[i][pkg.key]))
        status = html.escape(pkg.status)
        data_series = json.dumps(
            [{"week": row["week_start"], "downloads": int(row[pkg.key])} for row in rows],
            ensure_ascii=False,
            separators=(",", ":"),
        ).replace("</", "<\\/")
        cards.append(
            f"""
      <section class="chart-card">
        <div class="card-head">
          <div>
            <p class="eyebrow">{html.escape(pkg.role)} · {status}</p>
            <h2><span class="dot" style="background:{pkg.color}"></span>{html.escape(pkg.name)}</h2>
          </div>
          <dl class="card-metrics">
            <div><dt>Chart total</dt><dd data-chart-total>{fmt_int(chart_total)}</dd></div>
            <div><dt>Latest full week</dt><dd>{fmt_int(latest_value)}</dd></div>
            <div><dt>Peak week</dt><dd>{html.escape(str(rows[peak_idx]["week_start"]))} / {compact(values[peak_idx])}</dd></div>
          </dl>
        </div>
        <div class="chart-toolbar">
          <label>
            <span>Start week</span>
            <input class="range-start" type="date" min="{min_week}" max="{max_week}" value="{min_week}" aria-label="Start week for {html.escape(pkg.name)}">
          </label>
          <button type="button" class="reset-range">Reset</button>
        </div>
        <div class="chart-wrap" data-chart data-package="{html.escape(pkg.name)}" data-color="{pkg.color}" data-series='{html.escape(data_series, quote=True)}'>
          <svg viewBox="0 0 1040 330" role="img" aria-label="{html.escape(pkg.name)} weekly PyPI downloads line chart"></svg>
          <div class="chart-tooltip" role="status"></div>
        </div>
        <p class="note">{html.escape(pkg.note)}</p>
      </section>
""".rstrip()
        )
    return "\n".join(cards)


def build_html(config: PageConfig) -> str:
    rows = read_rows(config.csv_file)
    metrics = page_metrics(rows, config)
    data_json = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    package_json = json.dumps(
        [{"key": pkg.key, "name": pkg.name, "role": pkg.role, "color": pkg.color, "status": pkg.status} for pkg in config.packages],
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    generated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(config.title)}</title>
  <style>
    :root {{
      --bg: #f5f7fa;
      --panel: #ffffff;
      --panel-soft: #f9fafb;
      --ink: #1f242b;
      --muted: #667085;
      --line: #d9e1ea;
      --line-soft: #ecf1f6;
      --teal: #126c73;
      --copper: #a45a2a;
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
    header, .chart-card, .summary-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    header {{ padding: 24px 26px; }}
    .label {{
      color: var(--teal);
      font-size: 12px;
      font-weight: 750;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    h1, h2, h3, p {{ margin: 0; }}
    h1 {{ margin-top: 7px; font-size: 32px; line-height: 1.16; letter-spacing: 0; }}
    .lede {{ margin-top: 10px; max-width: 980px; color: var(--muted); line-height: 1.6; }}
    .interpretation {{
      margin-top: 16px;
      padding: 14px 16px;
      border-left: 4px solid var(--copper);
      background: var(--panel-soft);
      color: #334155;
      line-height: 1.62;
    }}
    .source-line {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; color: var(--muted); }}
    .source-line span {{
      border: 1px solid var(--line);
      background: var(--panel-soft);
      border-radius: 999px;
      padding: 6px 10px;
      white-space: nowrap;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-top: 16px;
    }}
    .summary-card {{ padding: 14px; box-shadow: none; }}
    .summary-card span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 8px; }}
    .summary-card strong {{ display: block; font-size: 20px; line-height: 1.15; overflow-wrap: anywhere; }}
    .chart-grid {{ display: grid; grid-template-columns: minmax(0, 1fr); gap: 16px; margin-top: 16px; }}
    .chart-card {{ padding: 18px; min-width: 0; }}
    .card-head {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: start; }}
    .eyebrow {{ color: var(--muted); font-size: 12px; font-weight: 700; margin-bottom: 6px; }}
    h2 {{ display: flex; align-items: center; gap: 8px; font-size: 20px; line-height: 1.2; letter-spacing: 0; overflow-wrap: anywhere; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex: 0 0 auto; }}
    .card-metrics {{ display: grid; grid-template-columns: repeat(3, minmax(110px, 1fr)); gap: 8px; margin: 0; }}
    .card-metrics div {{ border: 1px solid var(--line-soft); background: var(--panel-soft); border-radius: 8px; padding: 10px; }}
    .card-metrics dt {{ color: var(--muted); font-size: 11px; margin-bottom: 5px; }}
    .card-metrics dd {{ margin: 0; font-weight: 750; font-size: 14px; overflow-wrap: anywhere; }}
    .chart-toolbar {{ display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin: 14px 0 10px; }}
    .chart-toolbar label {{ display: inline-flex; align-items: center; gap: 8px; color: var(--muted); font-size: 12px; }}
    .range-start {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      padding: 6px 8px;
      font: inherit;
    }}
    .reset-range {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel-soft);
      color: var(--ink);
      padding: 6px 10px;
      cursor: pointer;
    }}
    .chart-wrap {{ position: relative; width: 100%; min-width: 0; overflow-x: auto; }}
    .chart-wrap svg {{ display: block; width: 100%; min-width: 900px; height: auto; }}
    .axis {{ stroke: #c8d3df; stroke-width: 1; }}
    .grid {{ stroke: var(--line-soft); stroke-width: 1; }}
    .tick {{ stroke: #c8d3df; stroke-width: 1; }}
    .axis-label {{ fill: #667085; font-size: 11px; }}
    .chart-caption {{ fill: #475467; font-size: 12px; }}
    .empty-title {{ fill: #334155; font-size: 14px; font-weight: 700; }}
    .empty-subtitle {{ fill: #667085; font-size: 12px; }}
    .hover-overlay {{ cursor: crosshair; }}
    .hover-guide {{ stroke: #94a3b8; stroke-width: 1; stroke-dasharray: 4 4; pointer-events: none; }}
    .hover-point {{ pointer-events: none; }}
    .chart-tooltip {{
      position: absolute;
      z-index: 5;
      min-width: 170px;
      pointer-events: none;
      opacity: 0;
      transform: translateY(3px);
      transition: opacity 120ms ease, transform 120ms ease;
      background: rgba(15, 23, 42, 0.92);
      color: white;
      border-radius: 8px;
      padding: 9px 10px;
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.22);
      font-size: 12px;
      line-height: 1.45;
    }}
    .chart-tooltip.is-visible {{ opacity: 1; transform: translateY(0); }}
    .chart-tooltip strong {{ display: block; font-size: 13px; margin-bottom: 2px; }}
    .note {{
      margin-top: 12px;
      color: #334155;
      line-height: 1.58;
      background: var(--panel-soft);
      border: 1px solid var(--line-soft);
      border-radius: 8px;
      padding: 12px;
    }}
    footer {{ color: var(--muted); line-height: 1.6; margin: 18px 2px 0; font-size: 12px; }}
    @media (max-width: 1050px) {{
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .chart-grid {{ grid-template-columns: minmax(0, 1fr); }}
      .card-head {{ grid-template-columns: 1fr; }}
      .card-metrics {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    }}
    @media (max-width: 640px) {{
      .shell {{ padding: 16px; }}
      header, .chart-card {{ padding: 14px; }}
      h1 {{ font-size: 26px; }}
      .summary, .card-metrics {{ grid-template-columns: 1fr; }}
      .chart-toolbar {{ justify-content: flex-start; flex-wrap: wrap; }}
    }}
  </style>
  <link rel="stylesheet" href="dashboard_range_controls.css">
</head>
<body>
  <main class="shell">
    <header>
      <div class="label">{html.escape(config.label)}</div>
      <h1>{html.escape(config.title)}</h1>
      <p class="lede">{html.escape(config.source_note)}</p>
      <div class="interpretation"><strong>如何理解：</strong>{html.escape(config.interpretation)}</div>
      <div class="source-line">
        <span>CSV rows: {metrics["row_count"]}</span>
        <span>Week range: {html.escape(metrics["first_week"])} to {html.escape(metrics["last_week"])}</span>
        <span>Source latest date: {html.escape(config.source_last_date)}</span>
        <span>Latest complete week: {html.escape(metrics["complete_week"])}</span>
      </div>
      <section class="summary" aria-label="dashboard summary">
        <div class="summary-card"><span>Cumulative downloads</span><strong>{metrics["total_all"]}</strong></div>
        <div class="summary-card"><span>Latest full week total</span><strong>{metrics["latest_total"]}</strong></div>
        <div class="summary-card"><span>12w vs prior 12w</span><strong>{metrics["trailing_change"]}</strong></div>
        <div class="summary-card"><span>Largest latest-week package</span><strong>{html.escape(metrics["leader"])}</strong></div>
        <div class="summary-card"><span>Data source</span><strong>ClickPy / PyPI</strong></div>
      </section>
    </header>

    <section class="chart-grid" aria-label="package charts">
{package_cards(rows, config)}
    </section>

    <footer>
      Data source: {html.escape(config.source_label)}. Generated: {generated}. CSV file: {html.escape(config.csv_file)}.
      The final row may be a partial week when the source latest date is before that week's Sunday.
    </footer>
  </main>
  <script type="application/json" id="weekly-download-data">{data_json}</script>
  <script type="application/json" id="package-config">{package_json}</script>
  <script>
    (() => {{
      const SVG_NS = "http://www.w3.org/2000/svg";
      const numberFormat = new Intl.NumberFormat("en-US");

      function compactInt(value) {{
        if (value >= 1000000) return `${{(value / 1000000).toFixed(1)}}M`;
        if (value >= 1000) return `${{(value / 1000).toFixed(1)}}k`;
        return numberFormat.format(Math.round(value));
      }}

      function niceYMax(value) {{
        if (!Number.isFinite(value) || value <= 0) return 1;
        const rough = value / 4;
        const base = Math.pow(10, Math.floor(Math.log10(rough)));
        for (const step of [1, 2, 2.5, 5, 10]) {{
          const candidate = step * base * 4;
          if (candidate >= value) return candidate;
        }}
        return 10 * base * 4;
      }}

      function el(name, attrs = {{}}, text = null) {{
        const node = document.createElementNS(SVG_NS, name);
        for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
        if (text !== null) node.textContent = text;
        return node;
      }}

      function filteredRows(allRows, startInput) {{
        if (!allRows.length) return [];
        const minWeek = allRows[0].week;
        const maxWeek = allRows[allRows.length - 1].week;
        startInput.min = minWeek;
        startInput.max = maxWeek;
        if (!startInput.value) startInput.value = minWeek;
        return allRows.filter((row) => row.week >= startInput.value);
      }}

      function svgPoint(svg, event) {{
        const point = svg.createSVGPoint();
        point.x = event.clientX;
        point.y = event.clientY;
        return point.matrixTransform(svg.getScreenCTM().inverse());
      }}

      function showTooltip(wrap, event, row, packageName) {{
        const tooltip = wrap.querySelector(".chart-tooltip");
        const rect = wrap.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        tooltip.innerHTML = `<strong>${{packageName}}</strong><span>${{row.week}}</span><br>${{numberFormat.format(row.downloads)}} downloads`;
        tooltip.style.left = `${{Math.min(Math.max(x + 14, 8), rect.width - 190)}}px`;
        tooltip.style.top = `${{Math.max(y - 48, 8)}}px`;
        tooltip.classList.add("is-visible");
      }}

      function hideHover(wrap, guide, point) {{
        wrap.querySelector(".chart-tooltip").classList.remove("is-visible");
        guide.setAttribute("display", "none");
        point.setAttribute("display", "none");
      }}

      function renderChart(wrap) {{
        const card = wrap.closest(".chart-card");
        const startInput = card.querySelector(".range-start");
        const svg = wrap.querySelector("svg");
        const color = wrap.dataset.color;
        const packageName = wrap.dataset.package;
        const allRows = JSON.parse(wrap.dataset.series || "[]");
        const rows = filteredRows(allRows, startInput);
        const totalNode = card.querySelector("[data-chart-total]");
        if (totalNode) totalNode.textContent = numberFormat.format(rows.reduce((sum, row) => sum + row.downloads, 0));

        const width = 1040;
        const height = 330;
        const left = 72;
        const right = 28;
        const top = 34;
        const bottom = 56;
        const plotW = width - left - right;
        const plotH = height - top - bottom;

        svg.textContent = "";
        svg.setAttribute("viewBox", `0 0 ${{width}} ${{height}}`);
        svg.setAttribute("aria-label", `${{packageName}} weekly PyPI downloads line chart`);
        svg.appendChild(el("rect", {{ width, height, rx: 8, fill: "#ffffff" }}));

        if (!rows.length) {{
          svg.appendChild(el("text", {{ x: width / 2, y: height / 2 - 10, "text-anchor": "middle", class: "empty-title" }}, "No PyPI data"));
          svg.appendChild(el("text", {{ x: width / 2, y: height / 2 + 18, "text-anchor": "middle", class: "empty-subtitle" }}, "No weekly data in this range."));
          wrap.querySelector(".chart-tooltip").classList.remove("is-visible");
          return;
        }}

        const yMax = niceYMax(Math.max(...rows.map((row) => row.downloads)));
        const xAt = (index) => rows.length === 1 ? left + plotW / 2 : left + (index / (rows.length - 1)) * plotW;
        const yAt = (value) => top + plotH - (value / yMax) * plotH;

        for (let tick = 0; tick < 5; tick += 1) {{
          const value = Math.round(yMax * tick / 4);
          const y = yAt(value);
          svg.appendChild(el("line", {{ x1: left, x2: left + plotW, y1: y.toFixed(1), y2: y.toFixed(1), class: "grid" }}));
          svg.appendChild(el("text", {{ x: left - 12, y: (y + 4).toFixed(1), "text-anchor": "end", class: "axis-label" }}, compactInt(value)));
        }}

        const tickIndexes = new Set([0, rows.length - 1]);
        for (let i = 0; i < 6; i += 1) tickIndexes.add(Math.round(i * (rows.length - 1) / 5));
        [...tickIndexes].sort((a, b) => a - b).forEach((index) => {{
          const x = xAt(index);
          svg.appendChild(el("line", {{ x1: x.toFixed(1), x2: x.toFixed(1), y1: top + plotH, y2: top + plotH + 5, class: "tick" }}));
          svg.appendChild(el("text", {{ x: x.toFixed(1), y: top + plotH + 26, "text-anchor": "middle", class: "axis-label" }}, rows[index].week));
        }});

        svg.appendChild(el("line", {{ x1: left, x2: left + plotW, y1: top + plotH, y2: top + plotH, class: "axis" }}));
        svg.appendChild(el("line", {{ x1: left, x2: left, y1: top, y2: top + plotH, class: "axis" }}));

        const points = rows.map((row, index) => `${{xAt(index).toFixed(1)}},${{yAt(row.downloads).toFixed(1)}}`).join(" ");
        svg.appendChild(el("polyline", {{ points, fill: "none", stroke: color, "stroke-width": 2.7, "stroke-linejoin": "round", "stroke-linecap": "round" }}));

        const latest = rows[rows.length - 1];
        const peak = rows.reduce((best, row) => row.downloads > best.downloads ? row : best, rows[0]);
        svg.appendChild(el("text", {{ x: left, y: 20, class: "chart-caption" }}, `Weekly downloads, ${{rows[0].week}} to ${{latest.week}}`));
        svg.appendChild(el("text", {{ x: left + plotW, y: 20, "text-anchor": "end", class: "chart-caption" }}, `Latest: ${{latest.week}} / ${{numberFormat.format(latest.downloads)}} | Peak: ${{peak.week}} / ${{numberFormat.format(peak.downloads)}}`));

        const guide = el("line", {{ x1: left, x2: left, y1: top, y2: top + plotH, class: "hover-guide", display: "none" }});
        const point = el("circle", {{ cx: left, cy: top + plotH, r: 5, fill: "#ffffff", stroke: color, "stroke-width": 2.4, class: "hover-point", display: "none" }});
        svg.appendChild(guide);
        svg.appendChild(point);

        const overlay = el("rect", {{ x: left, y: top, width: plotW, height: plotH, fill: "transparent", class: "hover-overlay" }});
        overlay.addEventListener("pointermove", (event) => {{
          const local = svgPoint(svg, event);
          const rawIndex = rows.length === 1 ? 0 : Math.round(((local.x - left) / plotW) * (rows.length - 1));
          const index = Math.max(0, Math.min(rows.length - 1, rawIndex));
          const row = rows[index];
          const cx = xAt(index);
          const cy = yAt(row.downloads);
          guide.setAttribute("x1", cx.toFixed(1));
          guide.setAttribute("x2", cx.toFixed(1));
          guide.removeAttribute("display");
          point.setAttribute("cx", cx.toFixed(1));
          point.setAttribute("cy", cy.toFixed(1));
          point.removeAttribute("display");
          showTooltip(wrap, event, row, packageName);
        }});
        overlay.addEventListener("pointerleave", () => hideHover(wrap, guide, point));
        svg.appendChild(overlay);
      }}

      document.querySelectorAll("[data-chart]").forEach((wrap) => {{
        const card = wrap.closest(".chart-card");
        const startInput = card.querySelector(".range-start");
        const resetButton = card.querySelector(".reset-range");
        const minWeek = startInput.min || startInput.value;
        startInput.addEventListener("change", () => renderChart(wrap));
        resetButton.addEventListener("click", () => {{
          startInput.value = minWeek;
          renderChart(wrap);
        }});
        renderChart(wrap);
      }});
    }})();
  </script>
  <script src="dashboard_range_controls.js"></script>
</body>
</html>
"""


def build_page(output_name: str, source_last_date: str | None = None) -> str:
    config = next(config for config in PAGES if config.output == output_name)
    if source_last_date is not None:
        config = replace(config, source_last_date=source_last_date)
    return build_html(config)


def main() -> None:
    for config in PAGES:
        output = ROOT / config.output
        output.write_text(build_html(config), encoding="utf-8")
        print(f"wrote {output.name}")


if __name__ == "__main__":
    main()
