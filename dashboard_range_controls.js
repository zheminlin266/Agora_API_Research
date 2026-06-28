(() => {
  const SVG_NS = "http://www.w3.org/2000/svg";
  const numberFormat = new Intl.NumberFormat("en-US");

  const compactInt = (value) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${Math.round(value / 1000)}K`;
    return String(Math.round(value));
  };

  const dateKey = (day) => {
    const year = day.getFullYear();
    const month = String(day.getMonth() + 1).padStart(2, "0");
    const date = String(day.getDate()).padStart(2, "0");
    return `${year}-${month}-${date}`;
  };

  const mondayStart = (day) => {
    const copy = new Date(day);
    copy.setDate(copy.getDate() - ((copy.getDay() + 6) % 7));
    return dateKey(copy);
  };

  function rowIndexForWeek(allRows, week, preferEnd = false) {
    // ponytail: O(n) is enough for weekly dashboard rows; add a lookup only if this grows into thousands.
    if (preferEnd) {
      for (let index = allRows.length - 1; index >= 0; index -= 1) {
        if (allRows[index].week <= week) return index;
      }
      return 0;
    }
    const index = allRows.findIndex((row) => row.week >= week);
    return index === -1 ? allRows.length - 1 : index;
  }

  function defaultStartWeek(allRows, years, now = new Date()) {
    const cutoff = new Date(now.getFullYear() - years, now.getMonth(), now.getDate());
    const target = mondayStart(cutoff);
    if (target <= allRows[0].week) return allRows[0].week;
    if (target > allRows[allRows.length - 1].week) {
      return allRows[Math.max(0, allRows.length - years * 52)].week;
    }
    return allRows[rowIndexForWeek(allRows, target)].week;
  }

  function niceYMax(value) {
    if (value <= 0) return 1;
    const exponent = Math.floor(Math.log10(value));
    const base = 10 ** exponent;
    for (const multiplier of [1, 2, 5, 10]) {
      const candidate = multiplier * base;
      if (candidate >= value) return candidate;
    }
    return 10 * base;
  }

  function el(name, attrs = {}, text = null) {
    const node = document.createElementNS(SVG_NS, name);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
    if (text !== null) node.textContent = text;
    return node;
  }

  function ensureControls(card, wrap, allRows) {
    const minWeek = allRows[0].week;
    const maxWeek = allRows[allRows.length - 1].week;
    let toolbar = card.querySelector(".chart-toolbar");
    if (!toolbar) {
      toolbar = document.createElement("div");
      toolbar.className = "chart-toolbar";
    }

    let startInput = toolbar.querySelector(".range-start") || card.querySelector(".range-start");
    if (!startInput) {
      const label = document.createElement("label");
      label.innerHTML = `<span>Start week</span><input class="range-start" type="date">`;
      toolbar.appendChild(label);
      startInput = label.querySelector(".range-start");
    }

    let endInput = toolbar.querySelector(".range-end") || card.querySelector(".range-end");
    if (!endInput) {
      const label = document.createElement("label");
      label.innerHTML = `<span>End week</span><input class="range-end" type="date">`;
      toolbar.appendChild(label);
      endInput = label.querySelector(".range-end");
    }

    let panel = card.querySelector(".range-panel");
    if (!panel) {
      panel = document.createElement("div");
      panel.className = "range-panel";
      wrap.insertAdjacentElement("afterend", panel);
    }

    let brush = panel.querySelector("[data-range-brush]");
    if (!brush) {
      brush = document.createElement("div");
      brush.className = "range-brush";
      brush.dataset.rangeBrush = "";
      brush.innerHTML = `
        <input class="range-slider range-min" type="range" aria-label="Drag start week">
        <input class="range-slider range-max" type="range" aria-label="Drag end week">
      `;
      panel.appendChild(brush);
    }

    let labels = panel.querySelector(".range-labels");
    if (!labels) {
      labels = document.createElement("div");
      labels.className = "range-labels";
      labels.setAttribute("aria-hidden", "true");
      labels.innerHTML = `<span class="range-min-label"></span><span class="range-max-label"></span>`;
      panel.appendChild(labels);
    }

    panel.appendChild(toolbar);

    for (const input of [startInput, endInput]) {
      input.min = minWeek;
      input.max = maxWeek;
    }
    const startRange = brush.querySelector(".range-min");
    const endRange = brush.querySelector(".range-max");
    for (const input of [startRange, endRange]) {
      input.min = 0;
      input.max = allRows.length - 1;
      input.step = 1;
      input.disabled = !allRows.length;
    }

    return { panel, toolbar, brush, startInput, endInput, startRange, endRange };
  }

  function updateBrush(controls, allRows) {
    const max = Math.max(1, allRows.length - 1);
    const start = Number(controls.startRange.value);
    const end = Number(controls.endRange.value);
    controls.brush.style.setProperty("--range-left", `${(start / max) * 100}%`);
    controls.brush.style.setProperty("--range-right", `${100 - (end / max) * 100}%`);
    controls.panel.querySelector(".range-min-label").textContent = allRows[start]?.week || "";
    controls.panel.querySelector(".range-max-label").textContent = allRows[end]?.week || "";
  }

  function syncSlidersFromDates(controls, allRows) {
    let start = rowIndexForWeek(allRows, controls.startInput.value || allRows[0].week);
    let end = rowIndexForWeek(allRows, controls.endInput.value || allRows[allRows.length - 1].week, true);
    if (start > end) [start, end] = [end, start];
    controls.startRange.value = start;
    controls.endRange.value = end;
    controls.startInput.value = allRows[start].week;
    controls.endInput.value = allRows[end].week;
    updateBrush(controls, allRows);
  }

  function syncDatesFromSliders(controls, allRows, activeRange) {
    let start = Number(controls.startRange.value);
    let end = Number(controls.endRange.value);
    if (start > end) {
      if (activeRange === controls.startRange) end = start;
      else start = end;
    }
    controls.startRange.value = start;
    controls.endRange.value = end;
    controls.startInput.value = allRows[start].week;
    controls.endInput.value = allRows[end].week;
    updateBrush(controls, allRows);
  }

  function svgPoint(svg, event) {
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    return point.matrixTransform(svg.getScreenCTM().inverse());
  }

  function showTooltip(wrap, event, row) {
    const tooltip = wrap.querySelector(".chart-tooltip");
    if (!tooltip) return;
    const rect = wrap.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    tooltip.innerHTML = `<strong>${row.week}</strong><br>${numberFormat.format(row.downloads)} downloads`;
    tooltip.style.left = `${Math.min(Math.max(x + 14, 8), rect.width - 190)}px`;
    tooltip.style.top = `${Math.max(y - 44, 8)}px`;
    tooltip.classList.add("is-visible");
  }

  function hideHover(wrap, hoverGuide, hoverPoint) {
    const tooltip = wrap.querySelector(".chart-tooltip");
    if (tooltip) tooltip.classList.remove("is-visible");
    hoverGuide.setAttribute("display", "none");
    hoverPoint.setAttribute("display", "none");
  }

  function renderChart(wrap, controls, allRows) {
    const svg = wrap.querySelector("svg");
    const color = wrap.dataset.color || "#2563eb";
    const packageName = wrap.dataset.package || "package";
    const rows = allRows.filter((row) => row.week >= controls.startInput.value && row.week <= controls.endInput.value);
    const totalNode = wrap.closest(".chart-card")?.querySelector("[data-chart-total]");
    if (totalNode) totalNode.textContent = numberFormat.format(rows.reduce((sum, row) => sum + row.downloads, 0));

    const width = 1040, height = 330, left = 72, right = 28, top = 34, bottom = 56;
    const plotW = width - left - right, plotH = height - top - bottom;
    svg.textContent = "";
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("aria-label", `${packageName} weekly downloads line chart`);
    svg.appendChild(el("rect", { width, height, rx: 8, fill: "#ffffff" }));

    if (!rows.length) {
      svg.appendChild(el("text", { x: width / 2, y: height / 2 - 10, "text-anchor": "middle", class: "empty-title" }, "No data"));
      svg.appendChild(el("text", { x: width / 2, y: height / 2 + 18, "text-anchor": "middle", class: "empty-subtitle" }, "No complete-week data in this range."));
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
    svg.appendChild(el("polygon", { points: `${left},${top + plotH} ${points} ${left + plotW},${top + plotH}`, fill: color, opacity: 0.10 }));
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
      event.stopPropagation();
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
    overlay.addEventListener("mousemove", (event) => event.stopPropagation());
    overlay.addEventListener("pointerleave", (event) => {
      event.stopPropagation();
      hideHover(wrap, hoverGuide, hoverPoint);
    });
    svg.appendChild(overlay);
  }

  function enhanceChart(wrap) {
    if (wrap.dataset.rangeEnhanced === "1") return;
    const allRows = JSON.parse(wrap.dataset.series || "[]").map((row) => ({
      week: row.week || row.date || row.week_start,
      downloads: Number(row.downloads ?? row.value ?? 0),
    })).filter((row) => row.week);
    if (!allRows.length) return;
    const card = wrap.closest(".chart-card");
    if (!card) return;
    wrap.dataset.chart = "";
    wrap.dataset.package = wrap.dataset.package || card.querySelector("h2")?.textContent?.trim() || "package";
    if (!wrap.querySelector(".chart-tooltip")) {
      const tooltip = document.createElement("div");
      tooltip.className = "chart-tooltip";
      tooltip.setAttribute("role", "status");
      wrap.appendChild(tooltip);
    }
    const controls = ensureControls(card, wrap, allRows);
    if (!controls.startInput.value || controls.startInput.value === allRows[0].week) {
      controls.startInput.value = defaultStartWeek(allRows, Number(wrap.dataset.defaultYears || 2));
    }
    controls.endInput.value = controls.endInput.value || allRows[allRows.length - 1].week;
    syncSlidersFromDates(controls, allRows);

    const redraw = () => {
      syncSlidersFromDates(controls, allRows);
      renderChart(wrap, controls, allRows);
    };
    controls.startInput.addEventListener("change", redraw);
    controls.endInput.addEventListener("change", redraw);
    controls.startRange.addEventListener("input", () => {
      syncDatesFromSliders(controls, allRows, controls.startRange);
      renderChart(wrap, controls, allRows);
    });
    controls.endRange.addEventListener("input", () => {
      syncDatesFromSliders(controls, allRows, controls.endRange);
      renderChart(wrap, controls, allRows);
    });
    wrap.dataset.rangeEnhanced = "1";
    renderChart(wrap, controls, allRows);
  }

  function enhanceAllCharts() {
    document.getElementById("tooltip")?.remove();
    document.querySelectorAll("[data-chart], .chart-wrap[data-series]").forEach(enhanceChart);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhanceAllCharts);
  } else {
    enhanceAllCharts();
  }

  window.dashboardRangeControls = { defaultStartWeek, mondayStart, rowIndexForWeek };
})();
