import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const NPM_REGISTRY = "https://registry.npmjs.org";
const NPM_DOWNLOADS = "https://api.npmjs.org/downloads";
const EARLIEST_NPM_DOWNLOAD_DATE = "2015-01-10";
const MAX_RANGE_DAYS = 548;

const VENDORS = {
  twilio: {
    displayName: "Twilio",
    csv: "twilio_npm_weekly_downloads.csv",
    html: "twilio_npm_downloads_dashboard.html",
    metadata: "twilio_npm_downloads_metadata.json",
    packages: [
      "twilio-video",
      "@twilio/voice-sdk",
      "@twilio/video-react-native-sdk",
      "@twilio/video-processors",
      "twilio",
    ],
    descriptions: {
      "twilio-video": "Twilio Video JavaScript 浏览器端 SDK。",
      "@twilio/voice-sdk": "Twilio JavaScript Voice SDK，用于浏览器和应用内语音通话集成。",
      "@twilio/video-react-native-sdk": "Twilio Video 的 React Native WebRTC SDK。",
      "@twilio/video-processors": "Twilio Video 的 JavaScript 视频处理库，用于背景处理等视频效果。",
      twilio: "Twilio 通用 Node.js 辅助库，覆盖范围不限于实时音视频 API。",
    },
    notes: {
      "twilio-video": "浏览器视频 SDK 的需求信号，主要对应 Twilio Programmable Video 集成。周度 npm 下载量包含自动化安装，应理解为开发者兴趣，而不是实际使用量。",
      "@twilio/voice-sdk": "JavaScript Voice SDK 的需求信号，反映浏览器和应用内语音通话集成的开发者关注度。观察趋势和版本发布前后的变化比绝对值更重要。",
      "@twilio/video-react-native-sdk": "面向移动端 Twilio Video 集成的 React Native 视频 SDK 信号。序列缺失或读数较低可能来自包生命周期变化，不一定代表产品需求偏弱。",
      "@twilio/video-processors": "用于背景处理等效果的视频预处理包，有助于把附加媒体处理兴趣与核心视频 SDK 需求区分开。",
      twilio: "Twilio 通用 Node.js 辅助库，覆盖多类 Twilio API，不只代表 RTC；应与视频和语音 SDK 包分开比较。",
    },
  },
  bandwidth: {
    displayName: "Bandwidth",
    csv: "bandwidth_npm_weekly_downloads.csv",
    html: "bandwidth_npm_downloads_dashboard.html",
    metadata: "bandwidth_npm_downloads_metadata.json",
    packages: ["bandwidth-rtc", "@bandwidth/bw-webrtc-sdk", "bandwidth-sdk"],
    descriptions: {
      "bandwidth-rtc": "BandwidthRTC Node 应用 SDK。",
      "@bandwidth/bw-webrtc-sdk": "Bandwidth WebRTC SDK，用于浏览器实时通信集成。",
      "bandwidth-sdk": "Bandwidth SDK 的 OpenAPI 客户端，覆盖范围可能不限于 WebRTC。",
    },
    notes: {
      "bandwidth-rtc": "Bandwidth RTC 包的需求信号。如果 npm 元数据缺失，看板仍会保留该包并显示未找到状态。",
      "@bandwidth/bw-webrtc-sdk": "Bandwidth WebRTC SDK 包的需求信号，反映浏览器实时通信集成的开发者关注度。",
      "bandwidth-sdk": "Bandwidth 通用 SDK 的需求信号，可能包含非 WebRTC API 使用，因此应与 RTC 专用包分开解读。",
    },
  },
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const toDate = (value) => new Date(`${value}T00:00:00.000Z`);
const isoDate = (date) => date.toISOString().slice(0, 10);
const addDays = (date, days) => new Date(date.getTime() + days * 86400000);
const maxDate = (a, b) => (a > b ? a : b);

function weekStart(value) {
  const date = typeof value === "string" ? toDate(value) : value;
  const diff = (date.getUTCDay() + 6) % 7;
  return addDays(date, -diff);
}

function latestCompleteWeekStart(latestDay) {
  const currentWeek = weekStart(latestDay);
  return latestDay >= addDays(currentWeek, 6) ? currentWeek : addDays(currentWeek, -7);
}

function encodePackage(packageName) {
  return encodeURIComponent(packageName);
}

function htmlEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function csvEscape(value) {
  const text = String(value ?? "");
  if (/[",\n\r]/.test(text)) return `"${text.replaceAll('"', '""')}"`;
  return text;
}

function parseCsvLine(line) {
  const values = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (quoted && char === '"' && line[index + 1] === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values;
}

function readCsv(filePath) {
  const lines = fs.readFileSync(filePath, "utf8").trimEnd().split(/\r?\n/);
  const columns = parseCsvLine(lines[0]).map((column) => column.replace(/^\uFEFF/, ""));
  return lines.slice(1).map((line) => {
    const values = parseCsvLine(line);
    return Object.fromEntries(columns.map((column, index) => [column, values[index] ?? ""]));
  });
}

function formatInt(value) {
  if (value === null || value === undefined) return "-";
  return Number(value).toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function packageDescription(config, packageName, meta) {
  return config.descriptions?.[packageName] || meta.description || meta.error || "没有 npm registry 记录。";
}

async function fetchJson(url, retries = 6) {
  let lastError;
  for (let attempt = 0; attempt < retries; attempt += 1) {
    try {
      const response = await fetch(url, {
        headers: {
          Accept: "application/json",
          "User-Agent": "codex-vendor-npm-weekly-dashboard/1.0",
        },
      });
      if (response.status === 429 && attempt < retries - 1) {
        const retryAfter = Number(response.headers.get("retry-after"));
        const waitMs = Number.isFinite(retryAfter) ? retryAfter * 1000 : 30000 * (attempt + 1);
        await sleep(Math.max(waitMs, 30000));
        continue;
      }
      if (!response.ok) {
        const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
        error.status = response.status;
        error.statusText = response.statusText;
        throw error;
      }
      return response.json();
    } catch (error) {
      lastError = error;
      if (error.status && error.status !== 429) throw error;
      await sleep(1200 * (attempt + 1));
    }
  }
  throw new Error(`Failed to fetch ${url}: ${lastError?.message || lastError}`);
}

async function loadPackageMeta(packageName) {
  try {
    const data = await fetchJson(`${NPM_REGISTRY}/${encodePackage(packageName)}`);
    const createdRaw = data.time?.created || null;
    return {
      name: packageName,
      exists: true,
      created: createdRaw ? toDate(createdRaw.slice(0, 10)) : null,
      createdRaw,
      modifiedRaw: data.time?.modified || null,
      description: data.description || "",
      error: null,
    };
  } catch (error) {
    if (error.status === 404) {
      return {
        name: packageName,
        exists: false,
        created: null,
        createdRaw: null,
        modifiedRaw: null,
        description: "",
        error: `HTTP 404: ${error.statusText || "Not Found"}`,
      };
    }
    throw error;
  }
}

async function latestDownloadDay() {
  const data = await fetchJson(`${NPM_DOWNLOADS}/point/last-day`);
  return toDate(data.end);
}

function* iterRanges(start, end) {
  let current = start;
  while (current <= end) {
    const chunkEnd = current.getTime() + (MAX_RANGE_DAYS - 1) * 86400000 <= end.getTime()
      ? addDays(current, MAX_RANGE_DAYS - 1)
      : end;
    yield [current, chunkEnd];
    current = addDays(chunkEnd, 1);
  }
}

async function loadDailyDownloads(packageName, start, end) {
  const daily = new Map();
  for (const [chunkStart, chunkEnd] of iterRanges(start, end)) {
    const period = `${isoDate(chunkStart)}:${isoDate(chunkEnd)}`;
    const url = `${NPM_DOWNLOADS}/range/${period}/${encodePackage(packageName)}`;
    try {
      const payload = await fetchJson(url);
      for (const row of payload.downloads || []) {
        daily.set(row.day, Number(row.downloads || 0));
      }
    } catch (error) {
      if (error.status !== 404) throw error;
    }
    await sleep(1200);
  }
  return daily;
}

function weeklyFromDaily(daily) {
  const weekly = new Map();
  for (const [day, downloads] of daily.entries()) {
    const start = isoDate(weekStart(day));
    weekly.set(start, (weekly.get(start) || 0) + downloads);
  }
  return weekly;
}

function buildRows(packages, metas, weeklyData, latestDay) {
  const starts = Object.values(metas)
    .filter((meta) => meta.exists && meta.created)
    .map((meta) => weekStart(maxDate(meta.created, toDate(EARLIEST_NPM_DOWNLOAD_DATE))));
  if (!starts.length) return [];

  const firstWeek = starts.reduce((a, b) => (a < b ? a : b));
  const lastWeek = weekStart(latestDay);
  const rows = [];

  for (let current = firstWeek; current <= lastWeek; current = addDays(current, 7)) {
    const week = isoDate(current);
    const row = { week_start: week };
    for (const packageName of packages) {
      const meta = metas[packageName];
      const startWeek = meta.created ? weekStart(maxDate(meta.created, toDate(EARLIEST_NPM_DOWNLOAD_DATE))) : null;
      row[packageName] = !meta.exists || !startWeek || current < startWeek
        ? ""
        : String(weeklyData[packageName]?.get(week) || 0);
    }
    rows.push(row);
  }
  return rows;
}

function writeCsv(filePath, rows, packages) {
  const columns = ["week_start", ...packages];
  const lines = [columns.map(csvEscape).join(",")];
  for (const row of rows) {
    lines.push(columns.map((column) => csvEscape(row[column])).join(","));
  }
  fs.writeFileSync(filePath, `\ufeff${lines.join("\n")}\n`, "utf8");
}

function seriesForPackage(rows, packageName, completeThrough) {
  return rows
    .filter((row) => toDate(row.week_start) <= completeThrough && row[packageName] !== "")
    .map((row) => ({ week: row.week_start, downloads: Number(row[packageName]) }));
}

function chartShell(packageName, series, color) {
  const minWeek = series[0]?.week || "";
  const maxWeek = series.at(-1)?.week || "";
  const disabled = series.length ? "" : " disabled";
  return `
      <div class="chart-toolbar">
        <label><span>开始周</span><input class="range-start" type="date" min="${minWeek}" max="${maxWeek}" value="${minWeek}" aria-label="${htmlEscape(packageName)} 开始周"${disabled}></label>
        <label><span>结束周</span><input class="range-end" type="date" min="${minWeek}" max="${maxWeek}" value="${maxWeek}" aria-label="${htmlEscape(packageName)} 结束周"${disabled}></label>
      </div>
      <div class="chart-wrap" data-chart data-package="${htmlEscape(packageName)}" data-color="${color}" data-series="${htmlEscape(JSON.stringify(series))}">
        <svg viewBox="0 0 1040 330" role="img" aria-label="${htmlEscape(packageName)} 周下载量折线图"></svg>
        <div class="chart-tooltip" role="status"></div>
      </div>`;
}

function dashboardScript() {
  return `
  <script>
    (() => {
      const SVG_NS = "http://www.w3.org/2000/svg";
      const numberFormat = new Intl.NumberFormat("en-US");
      const compactInt = (value) => value >= 1000000 ? \`\${(value / 1000000).toFixed(1)}M\` : value >= 1000 ? \`\${Math.round(value / 1000)}K\` : String(Math.round(value));
      function niceYMax(value) {
        if (value <= 0) return 1;
        const base = 10 ** Math.floor(Math.log10(value));
        for (const multiplier of [1, 2, 5, 10]) if (multiplier * base >= value) return multiplier * base;
        return 10 * base;
      }
      function el(name, attrs = {}, text = null) {
        const node = document.createElementNS(SVG_NS, name);
        for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
        if (text !== null) node.textContent = text;
        return node;
      }
      function filteredRows(allRows, startInput, endInput) {
        if (!allRows.length) return [];
        const minWeek = allRows[0].week;
        const maxWeek = allRows[allRows.length - 1].week;
        for (const input of [startInput, endInput]) {
          input.min = minWeek;
          input.max = maxWeek;
        }
        if (!startInput.value) startInput.value = minWeek;
        if (!endInput.value) endInput.value = maxWeek;
        let startWeek = startInput.value || minWeek;
        let endWeek = endInput.value || maxWeek;
        if (startWeek > endWeek) [startWeek, endWeek] = [endWeek, startWeek];
        return allRows.filter((row) => row.week >= startWeek && row.week <= endWeek);
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
        tooltip.innerHTML = \`<strong>\${row.week}</strong><br>\${numberFormat.format(row.downloads)} downloads\`;
        tooltip.style.left = \`\${Math.min(Math.max(x + 14, 8), rect.width - 190)}px\`;
        tooltip.style.top = \`\${Math.max(y - 44, 8)}px\`;
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
        const rows = filteredRows(JSON.parse(wrap.dataset.series || "[]"), startInput, endInput);
        const width = 1040, height = 330, left = 72, right = 28, top = 34, bottom = 56;
        const plotW = width - left - right, plotH = height - top - bottom;
        svg.textContent = "";
        svg.setAttribute("viewBox", \`0 0 \${width} \${height}\`);
        svg.setAttribute("aria-label", \`\${packageName} 周下载量折线图\`);
        svg.appendChild(el("rect", { width, height, rx: 8, fill: "#ffffff" }));
        if (!rows.length) {
          svg.appendChild(el("text", { x: width / 2, y: height / 2 - 10, "text-anchor": "middle", class: "empty-title" }, "暂无 npm 数据"));
          svg.appendChild(el("text", { x: width / 2, y: height / 2 + 18, "text-anchor": "middle", class: "empty-subtitle" }, "当前区间没有完整周数据。"));
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
        svg.appendChild(el("polyline", { points: rows.map((row, index) => \`\${xAt(index).toFixed(1)},\${yAt(row.downloads).toFixed(1)}\`).join(" "), fill: "none", stroke: color, "stroke-width": 2.6, "stroke-linejoin": "round", "stroke-linecap": "round" }));
        const latest = rows[rows.length - 1];
        const peak = rows.reduce((best, row) => row.downloads > best.downloads ? row : best, rows[0]);
        svg.appendChild(el("text", { x: left, y: 20, class: "chart-caption" }, \`周下载量，\${rows[0].week} 至 \${latest.week}\`));
        svg.appendChild(el("text", { x: left + plotW, y: 20, "text-anchor": "end", class: "chart-caption" }, \`最新: \${latest.week} / \${numberFormat.format(latest.downloads)} | 峰值: \${peak.week} / \${numberFormat.format(peak.downloads)}\`));
        const hoverGuide = el("line", { x1: left, x2: left, y1: top, y2: top + plotH, class: "hover-guide", display: "none" });
        const hoverPoint = el("circle", { cx: left, cy: top + plotH, r: 5, fill: "#ffffff", stroke: color, "stroke-width": 2.4, class: "hover-point", display: "none" });
        svg.appendChild(hoverGuide);
        svg.appendChild(hoverPoint);
        const overlay = el("rect", { x: left, y: top, width: plotW, height: plotH, fill: "transparent", class: "hover-overlay" });
        overlay.addEventListener("pointermove", (event) => {
          const local = svgPoint(svg, event);
          const rawIndex = rows.length === 1 ? 0 : Math.round(((local.x - left) / plotW) * (rows.length - 1));
          const index = Math.max(0, Math.min(rows.length - 1, rawIndex));
          const row = rows[index], cx = xAt(index), cy = yAt(row.downloads);
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
  </script>`;
}

function buildHtml(vendor, config, rows, metas, latestDay) {
  const completeThrough = latestCompleteWeekStart(latestDay);
  const colors = ["#2563eb", "#d97706", "#0f766e", "#be123c", "#475569", "#7c3aed", "#0891b2"];
  const firstWeek = rows[0]?.week_start || "-";
  const lastWeek = rows.at(-1)?.week_start || "-";
  const chartLastWeek = isoDate(completeThrough);
  const cards = config.packages.map((packageName, index) => {
    const series = seriesForPackage(rows, packageName, completeThrough);
    const total = series.length ? series.reduce((sum, row) => sum + row.downloads, 0) : null;
    const latest = series.length ? series.at(-1).downloads : null;
    const nonZero = series.filter((row) => row.downloads > 0).length;
    const meta = metas[packageName];
    return `
            <section class="chart-card">
              <div class="card-head">
                <div>
                  <h2>${htmlEscape(packageName)}</h2>
                  <p>${htmlEscape(packageDescription(config, packageName, meta))}</p>
                </div>
                <dl class="metrics">
                  <div><dt>状态</dt><dd>${meta.exists ? "已找到" : "未找到"}</dd></div>
                  <div><dt>创建日期</dt><dd>${meta.createdRaw ? htmlEscape(meta.createdRaw.slice(0, 10)) : "-"}</dd></div>
                  <div><dt>图表合计</dt><dd>${formatInt(total)}</dd></div>
                  <div><dt>最新完整周</dt><dd>${formatInt(latest)}</dd></div>
                  <div><dt>非零周数</dt><dd>${formatInt(nonZero)}</dd></div>
                </dl>
              </div>
              ${chartShell(packageName, series, colors[index % colors.length])}
              <p class="note">${htmlEscape(config.notes[packageName] || "周度 npm 下载量适合作为开发者需求方向性指标，不应直接等同于客户数或运行时使用量。")}</p>
            </section>`;
  });
  const metadataRows = config.packages.map((packageName) => {
    const meta = metas[packageName];
    return `
            <tr>
              <td>${htmlEscape(packageName)}</td>
              <td>${meta.exists ? "是" : "否"}</td>
              <td>${htmlEscape(meta.createdRaw || "-")}</td>
              <td>${htmlEscape(meta.modifiedRaw || "-")}</td>
              <td>${htmlEscape(packageDescription(config, packageName, meta))}</td>
            </tr>`;
  });

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${htmlEscape(config.displayName)} npm 周下载量看板</title>
  <style>
    :root { --ink: #162033; --muted: #596579; --line: #dbe2ea; --soft: #f5f7fb; --panel: #ffffff; --accent: #2563eb; }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f7f8fb; color: var(--ink); }
    main { width: min(1180px, calc(100vw - 32px)); margin: 0 auto; padding: 32px 0 48px; }
    header { margin-bottom: 22px; }
    h1 { margin: 0 0 8px; font-size: 30px; line-height: 1.2; letter-spacing: 0; }
    .subtitle { margin: 0; color: var(--muted); font-size: 14px; line-height: 1.6; }
    .summary { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 20px 0 24px; }
    .summary div, .source-box { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; }
    .summary span { display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }
    .summary strong { font-size: 18px; font-weight: 700; }
    .chart-card { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 20px; margin-bottom: 18px; }
    .card-head { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 18px; align-items: start; margin-bottom: 10px; }
    h2 { margin: 0 0 4px; font-size: 20px; line-height: 1.25; letter-spacing: 0; }
    .card-head p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
    .metrics { display: grid; grid-template-columns: repeat(5, minmax(86px, auto)); gap: 8px; margin: 0; }
    .metrics div { border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; background: #fbfcfe; }
    dt { color: var(--muted); font-size: 11px; margin-bottom: 3px; }
    dd { margin: 0; font-size: 13px; font-weight: 700; white-space: nowrap; }
    .chart-toolbar { display: flex; justify-content: flex-end; align-items: center; flex-wrap: wrap; gap: 10px; margin: 10px 0 8px; }
    .chart-toolbar label { display: inline-flex; align-items: center; gap: 8px; color: var(--muted); font-size: 12px; font-weight: 650; }
    .range-start, .range-end { border: 1px solid var(--line); border-radius: 6px; background: #ffffff; color: var(--ink); font-size: 13px; padding: 6px 9px; }
    .chart-wrap { width: 100%; overflow-x: auto; position: relative; }
    svg { width: 100%; min-width: 760px; height: auto; display: block; }
    .grid { stroke: #e7ecf2; stroke-width: 1; }
    .axis, .tick { stroke: #98a3b3; stroke-width: 1; }
    .axis-label { fill: #667085; font-size: 12px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    .chart-caption { fill: #475467; font-size: 12px; font-weight: 650; }
    .hover-overlay { cursor: crosshair; }
    .hover-guide { stroke: #94a3b8; stroke-width: 1; stroke-dasharray: 3 5; opacity: 0.85; }
    .hover-point { pointer-events: none; }
    .chart-tooltip { position: absolute; z-index: 5; min-width: 150px; pointer-events: none; opacity: 0; transform: translateY(4px); transition: opacity 120ms ease, transform 120ms ease; border: 1px solid #cbd5e1; border-radius: 6px; background: #ffffff; box-shadow: 0 10px 26px rgba(15, 23, 42, 0.16); color: var(--ink); font-size: 12px; line-height: 1.45; padding: 8px 10px; }
    .chart-tooltip.is-visible { opacity: 1; transform: translateY(0); }
    .empty-title { fill: #334155; font-size: 24px; font-weight: 700; }
    .empty-subtitle { fill: #667085; font-size: 14px; }
    .note { margin: 12px 0 0; color: #334155; font-size: 14px; line-height: 1.65; background: var(--soft); border-left: 3px solid var(--accent); padding: 10px 12px; }
    .source-box { margin-top: 18px; }
    .source-box h2 { margin-bottom: 10px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { border-top: 1px solid var(--line); padding: 9px 8px; text-align: left; vertical-align: top; }
    th { color: #475467; font-weight: 700; background: #fbfcfe; }
    code { background: #eef2f7; padding: 2px 5px; border-radius: 4px; }
    @media (max-width: 860px) {
      main { width: min(100vw - 20px, 1180px); padding-top: 20px; }
      .summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .card-head { grid-template-columns: 1fr; }
      .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      h1 { font-size: 24px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>${htmlEscape(config.displayName)} npm 周下载量看板</h1>
      <p class="subtitle">数据来自官方 npm downloads API，并按周一开始的自然周汇总。CSV 文件保留最新未完整周；HTML 图表只展示完整周。npm 下载量包含 CI、镜像、机器人和缓存影响，因此更适合作为开发者需求的方向性信号，而不是客户数量或实际运行使用量。</p>
    </header>
    <section class="summary" aria-label="dashboard summary">
      <div><span>CSV 行数</span><strong>${rows.length}</strong></div>
      <div><span>周度范围</span><strong>${firstWeek} 至 ${lastWeek}</strong></div>
      <div><span>图表截至</span><strong>${chartLastWeek}</strong></div>
      <div><span>最新 npm 日期</span><strong>${isoDate(latestDay)}</strong></div>
    </section>
    ${cards.join("")}
    <section class="source-box">
      <h2>来源与包元数据</h2>
      <table>
        <thead><tr><th>包名</th><th>是否找到</th><th>创建时间</th><th>更新时间</th><th>说明 / 错误</th></tr></thead>
        <tbody>${metadataRows.join("")}</tbody>
      </table>
      <p class="subtitle">输出 CSV: <code>${htmlEscape(config.csv)}</code>。元数据 JSON: <code>${htmlEscape(config.metadata)}</code>。图表显示至完整周 <code>${chartLastWeek}</code>。</p>
    </section>
  </main>
  ${dashboardScript()}
</body>
</html>
`;
}

function writeMetadata(vendor, config, metas, rows, latestDay) {
  const metadata = {
    generated_at_utc: new Date().toISOString(),
    vendor,
    source: {
      registry: NPM_REGISTRY,
      downloads: NPM_DOWNLOADS,
      range_limit_note: `npm downloads API 按 ${MAX_RANGE_DAYS} 天分段查询。`,
      weekly_grain: "周一开始的自然周",
      latest_download_day: isoDate(latestDay),
      html_chart_complete_through_week_start: isoDate(latestCompleteWeekStart(latestDay)),
      html_chart_policy: "HTML 折线图排除最新未完整周；CSV 保留全部周度汇总。",
      caveat: "npm 下载量包含自动化、镜像、机器人和缓存影响。",
    },
    csv: {
      path: path.join(ROOT, config.csv),
      rows: rows.length,
      columns: ["week_start", ...config.packages],
    },
    packages: Object.fromEntries(Object.entries(metas).map(([name, meta]) => [name, {
      exists: meta.exists,
      created: meta.createdRaw,
      modified: meta.modifiedRaw,
      description: packageDescription(config, name, meta),
      error: meta.error,
    }])),
  };
  fs.writeFileSync(path.join(ROOT, config.metadata), `${JSON.stringify(metadata, null, 2)}\n`, "utf8");
}

async function buildVendor(vendor, latestDay) {
  const config = VENDORS[vendor];
  const metas = Object.fromEntries(await Promise.all(config.packages.map(async (packageName) => [packageName, await loadPackageMeta(packageName)])));
  const weeklyData = {};
  for (const packageName of config.packages) {
    const meta = metas[packageName];
    if (!meta.exists || !meta.created) {
      weeklyData[packageName] = new Map();
      continue;
    }
    const start = maxDate(meta.created, toDate(EARLIEST_NPM_DOWNLOAD_DATE));
    weeklyData[packageName] = weeklyFromDaily(await loadDailyDownloads(packageName, start, latestDay));
  }
  const rows = buildRows(config.packages, metas, weeklyData, latestDay);
  writeCsv(path.join(ROOT, config.csv), rows, config.packages);
  fs.writeFileSync(path.join(ROOT, config.html), buildHtml(vendor, config, rows, metas, latestDay), "utf8");
  writeMetadata(vendor, config, metas, rows, latestDay);
  return {
    vendor,
    csv: path.join(ROOT, config.csv),
    html: path.join(ROOT, config.html),
    metadata: path.join(ROOT, config.metadata),
    rows: rows.length,
    packages: Object.fromEntries(Object.entries(metas).map(([name, meta]) => [name, { exists: meta.exists, created: meta.createdRaw }])),
  };
}

function buildVendorFromExisting(vendor) {
  const config = VENDORS[vendor];
  const metadata = JSON.parse(fs.readFileSync(path.join(ROOT, config.metadata), "utf8"));
  const rows = readCsv(path.join(ROOT, config.csv));
  const metas = Object.fromEntries(config.packages.map((packageName) => {
    const packageMeta = metadata.packages?.[packageName] || {};
    return [packageName, {
      exists: Boolean(packageMeta.exists),
      created: packageMeta.created ? new Date(packageMeta.created) : null,
      createdRaw: packageMeta.created || null,
      modifiedRaw: packageMeta.modified || null,
      description: packageMeta.description || "",
      error: packageMeta.error || null,
    }];
  }));
  const latestDay = toDate(metadata.source?.latest_download_day || rows.at(-1)?.week_start || isoDate(new Date()));
  fs.writeFileSync(path.join(ROOT, config.html), buildHtml(vendor, config, rows, metas, latestDay), "utf8");
  writeMetadata(vendor, config, metas, rows, latestDay);
  return {
    vendor,
    csv: path.join(ROOT, config.csv),
    html: path.join(ROOT, config.html),
    metadata: path.join(ROOT, config.metadata),
    rows: rows.length,
  };
}

const fromExisting = process.argv.includes("--from-existing");
const results = [];
let latestDay = null;
if (fromExisting) {
  for (const vendor of Object.keys(VENDORS)) {
    results.push(buildVendorFromExisting(vendor));
  }
} else {
  latestDay = await latestDownloadDay();
  for (const vendor of Object.keys(VENDORS)) {
    results.push(await buildVendor(vendor, latestDay));
  }
}
console.log(JSON.stringify({ mode: fromExisting ? "from-existing" : "refresh", latest_download_day: latestDay ? isoDate(latestDay) : null, results }, null, 2));
