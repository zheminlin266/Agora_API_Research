const dashboard = document.querySelector('#dashboard');
const statusNode = document.querySelector('#dashboardStatus');
const completeWeekNode = document.querySelector('#completeWeek');
const packageCountNode = document.querySelector('#packageCount');
const rangeDescriptionNode = document.querySelector('#rangeDescription');
const rangeButtons = [...document.querySelectorAll('[data-range]')];

const DATASETS = {
  agoraNpm: ['./Data/agora_npm_weekly_downloads.csv', './json/agora_npm_downloads_metadata.json', 'npm'],
  agoraPypi: ['./Data/agora_pypi_weekly_downloads.csv', './json/agora_pypi_downloads_metadata.json', 'PyPI'],
  livekitNpm: ['./Data/livekit_npm_weekly_downloads.csv', './json/livekit_npm_downloads_metadata.json', 'npm'],
  livekitPypi: ['./Data/livekit_pypi_weekly_downloads.csv', './json/livekit_pypi_downloads_metadata.json', 'PyPI'],
  twilioNpm: ['./Data/twilio_npm_weekly_downloads.csv', './json/twilio_npm_downloads_metadata.json', 'npm'],
  rtcNpm: ['./Data/rtc_competitor_npm_weekly_downloads.csv', './json/rtc_competitor_npm_downloads_metadata.json', 'npm']
};

const PACKAGES = [
  ['agora', 'agoraNpm', 'agora-rtc-sdk-ng', 'agora-rtc-sdk-ng', '浏览器实时音视频 Web SDK，用于视频会议、互动直播、语音通话和在线课堂等低延迟场景。'],
  ['agora', 'agoraNpm', 'agora-rtm-sdk', 'agora-rtm-sdk', '实时消息 SDK，用于频道信令、聊天、在线状态与呼叫邀请，常与 RTC 音视频能力配合。'],
  ['agora', 'agoraNpm', 'agora-rtc-react', 'agora-rtc-react', 'React 封装与组件，用于在 React 应用中快速接入音视频房间、设备管理和通话状态。'],
  ['agora', 'agoraNpm', 'react-native-agora', 'react-native-agora', 'React Native RTC SDK，用于 iOS、Android 跨平台应用中的语音通话、视频会议和直播互动。'],
  ['agora', 'agoraPypi', 'agora-token-builder', 'agora-token-builder', 'Python Token 生成工具，用于服务端签发 RTC、RTM 鉴权令牌，控制用户加入频道与访问权限。'],
  ['agora', 'agoraPypi', 'agora-python-server-sdk', 'agora-python-server-sdk', 'Python 服务端 SDK，用于后台管理房间、用户及云端能力，适合自动化服务和业务后端集成。'],
  ['livekit', 'livekitNpm', 'livekit-client', 'livekit-client', 'JavaScript、TypeScript 核心客户端，用于浏览器或 Node.js 接入房间、音视频轨道和实时数据。'],
  ['livekit', 'livekitNpm', '@livekit/components-react', 'livekit/components-react', 'LiveKit React UI 组件，用于快速搭建视频会议、语音房间、设备控制和参与者界面。'],
  ['livekit', 'livekitNpm', '@livekit/react-native', 'livekit/react-native', 'LiveKit React Native SDK，用于 iOS、Android 跨平台应用中的实时音视频房间与数据通信。'],
  ['livekit', 'livekitNpm', '@livekit/agents', 'livekit/agents', 'JavaScript、TypeScript Agent 框架，用于构建实时语音 AI、电话机器人及低延迟多模态交互服务。'],
  ['livekit', 'livekitNpm', '@livekit/agents-plugin-silero', 'livekit/agents-plugin-silero', 'LiveKit Agents 的 Silero VAD 插件，用于检测用户开始或停止说话，改善语音 Agent 轮次切换。'],
  ['livekit', 'livekitPypi', 'livekit', 'livekit', 'Python 实时 SDK，用于后端或 Agent 服务处理房间、音视频轨道、数据消息与实时任务。'],
  ['livekit', 'livekitPypi', 'livekit-api', 'livekit-api', 'Python 服务端 API 客户端，用于创建房间、管理参与者、生成令牌及调用云端管理接口。'],
  ['livekit', 'livekitPypi', 'livekit-agents', 'livekit-agents', 'Python Agents 框架，用于开发实时语音助手、呼叫机器人和接入 STT、LLM、TTS 的工作流。'],
  ['twilio', 'twilioNpm', '@twilio/voice-sdk', 'twilio/voice-sdk', '浏览器与应用内语音通话 SDK，用于软电话、客服坐席、点击呼叫和 PSTN 通话控制。'],
  ['twilio', 'twilioNpm', 'twilio', 'twilio', 'Twilio Node.js 服务端库，用于短信、语音、视频及验证等 API 的鉴权、请求和后台自动化。'],
  ['tencent', 'rtcNpm', 'trtc-cloud-js-sdk', 'trtc-cloud-js-sdk', '腾讯 TRTC Web SDK，用于浏览器和 Electron 的视频会议、互动直播、语音通话及低延迟连麦。']
].map(([vendor, dataset, key, label, description]) => ({ vendor, dataset, key, label, description }));

const state = { range: '3y', datasets: new Map() };
const SVG_NS = 'http://www.w3.org/2000/svg';
const exact = new Intl.NumberFormat('en-US');
const compact = new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 });
const dateLabel = new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: 'short', timeZone: 'UTC' });

function parseCsv(text) {
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = headerLine.replace(/^\uFEFF/, '').split(',');
  return lines.filter(Boolean).map(line => {
    const cells = line.split(',');
    return Object.fromEntries(headers.map((header, index) => {
      const value = cells[index] ?? '';
      return [header, header === 'week_start' ? value : value === '' ? null : Number(value)];
    }));
  });
}

function completeWeek(metadata, rows) {
  return metadata?.source?.latest_complete_week_start
    ?? metadata?.source?.html_chart_complete_through_week_start
    ?? metadata?.dataset?.latest_complete_week_start
    ?? rows.at(-1)?.week_start;
}

async function loadDataset(name, [csvUrl, metadataUrl, registry]) {
  const [csvResponse, metadataResponse] = await Promise.all([fetch(csvUrl), fetch(metadataUrl)]);
  if (!csvResponse.ok) throw new Error(`${name}: CSV ${csvResponse.status}`);
  const rows = parseCsv(await csvResponse.text());
  const metadata = metadataResponse.ok ? await metadataResponse.json() : {};
  return { rows, metadata, registry, completeWeek: completeWeek(metadata, rows) };
}

function visibleRows(rows) {
  if (state.range === 'all' || rows.length === 0) return rows;
  const end = Date.parse(`${rows.at(-1).week_start}T00:00:00Z`);
  const years = state.range === '1y' ? 1 : 3;
  const start = new Date(end);
  start.setUTCFullYear(start.getUTCFullYear() - years);
  return rows.filter(row => Date.parse(`${row.week_start}T00:00:00Z`) >= start.getTime());
}

function svgElement(name, attributes = {}, text = '') {
  const node = document.createElementNS(SVG_NS, name);
  Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
  if (text) node.textContent = text;
  return node;
}

function niceMax(value) {
  if (value <= 0) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  return [1, 2, 5, 10].map(step => step * magnitude).find(step => step >= value) ?? value;
}

function drawChart(frame, rows, key) {
  const series = visibleRows(rows).filter(row => Number.isFinite(row[key]));
  if (!series.length) {
    frame.innerHTML = '<p class="chart-empty">当前范围没有可用数据</p>';
    return;
  }

  const width = 720, height = 220, left = 54, right = 12, top = 12, bottom = 32;
  const plotWidth = width - left - right, plotHeight = height - top - bottom;
  const yMax = niceMax(Math.max(...series.map(row => row[key])));
  const x = index => series.length === 1 ? left + plotWidth / 2 : left + index * plotWidth / (series.length - 1);
  const y = value => top + plotHeight - value * plotHeight / yMax;
  const svg = svgElement('svg', { viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': `${key} 周度下载趋势` });

  for (let index = 0; index <= 4; index += 1) {
    const value = yMax * index / 4;
    const yPos = y(value);
    svg.append(svgElement('line', { x1: left, x2: width - right, y1: yPos, y2: yPos, class: 'chart-grid' }));
    svg.append(svgElement('text', { x: left - 9, y: yPos + 4, 'text-anchor': 'end', class: 'axis-label' }, compact.format(value)));
  }

  const labelIndexes = [...new Set([0, Math.floor((series.length - 1) / 2), series.length - 1])];
  labelIndexes.forEach((index, labelIndex) => {
    svg.append(svgElement('text', {
      x: x(index), y: height - 8, 'text-anchor': labelIndex === 0 ? 'start' : labelIndex === 2 ? 'end' : 'middle',
      class: labelIndex === 1 ? 'axis-label axis-label-mid' : 'axis-label'
    }, dateLabel.format(new Date(`${series[index].week_start}T00:00:00Z`))));
  });

  svg.append(svgElement('line', { x1: left, x2: width - right, y1: top + plotHeight, y2: top + plotHeight, class: 'chart-axis' }));
  const points = series.map((row, index) => `${x(index)},${y(row[key])}`).join(' ');
  svg.append(svgElement('polyline', { points, class: 'chart-line' }));
  const last = series.at(-1);
  svg.append(svgElement('circle', { cx: x(series.length - 1), cy: y(last[key]), r: 3.5, class: 'chart-endpoint' }));

  const guide = svgElement('line', { y1: top, y2: top + plotHeight, class: 'chart-guide' });
  const point = svgElement('circle', { r: 4, class: 'chart-hover-point' });
  const hit = svgElement('rect', { x: left, y: top, width: plotWidth, height: plotHeight, class: 'chart-hit' });
  const tooltip = document.createElement('div');
  tooltip.className = 'chart-tooltip';

  hit.addEventListener('pointermove', event => {
    const bounds = svg.getBoundingClientRect();
    const relativeX = Math.max(0, Math.min(plotWidth, (event.clientX - bounds.left) * width / bounds.width - left));
    const index = series.length === 1 ? 0 : Math.round(relativeX / plotWidth * (series.length - 1));
    const row = series[index], xPos = x(index), yPos = y(row[key]);
    guide.setAttribute('x1', xPos); guide.setAttribute('x2', xPos); guide.style.opacity = '1';
    point.setAttribute('cx', xPos); point.setAttribute('cy', yPos); point.style.opacity = '1';
    tooltip.innerHTML = `<strong>${row.week_start}</strong><span>${exact.format(row[key])} downloads</span>`;
    tooltip.style.left = `${Math.min(frame.clientWidth - 150, Math.max(8, event.clientX - frame.getBoundingClientRect().left + 12))}px`;
    tooltip.style.top = `${Math.max(8, event.clientY - frame.getBoundingClientRect().top - 48)}px`;
    tooltip.classList.add('is-visible');
  });
  hit.addEventListener('pointerleave', () => {
    guide.style.opacity = '0'; point.style.opacity = '0'; tooltip.classList.remove('is-visible');
  });
  svg.append(guide, point, hit);
  frame.replaceChildren(svg, tooltip);
}

function renderCard(definition) {
  const dataset = state.datasets.get(definition.dataset);
  const rows = dataset?.rows.filter(row => row.week_start <= dataset.sharedCompleteWeek) ?? [];
  const values = rows.filter(row => Number.isFinite(row[definition.key]));
  const latest = values.at(-1)?.[definition.key];
  const previous = values.at(-53)?.[definition.key];
  const change = Number.isFinite(previous) && previous !== 0 ? (latest / previous - 1) * 100 : null;
  const article = document.createElement('article');
  article.className = 'package-chart';
  article.innerHTML = `
    <div class="package-head">
      <div class="package-name"><h3>${definition.label}</h3><p>${dataset?.registry ?? ''}</p></div>
      <div class="metric"><span>最新周</span><strong>${Number.isFinite(latest) ? compact.format(latest) : '—'}</strong></div>
      <div class="metric"><span>同比</span><strong class="${change === null ? 'is-muted' : ''}">${change === null ? '—' : `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`}</strong></div>
    </div>
    <div class="chart-frame"></div>
    <p class="package-description"><strong>功能与场景：</strong>${definition.description}</p>`;
  drawChart(article.querySelector('.chart-frame'), rows, definition.key);
  return article;
}

function render() {
  document.querySelectorAll('.chart-list').forEach(list => list.replaceChildren());
  PACKAGES.forEach(definition => {
    document.querySelector(`[data-vendor="${definition.vendor}"]`)?.append(renderCard(definition));
  });
  rangeDescriptionNode.textContent = state.range === 'all' ? '全部历史' : `最近 ${state.range === '1y' ? 1 : 3} 年`;
  rangeButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.range === state.range)));
}

async function initialize() {
  packageCountNode.textContent = String(PACKAGES.length);
  const results = await Promise.allSettled(
    Object.entries(DATASETS).map(async ([name, definition]) => [name, await loadDataset(name, definition)])
  );
  const errors = [];
  results.forEach(result => {
    if (result.status === 'fulfilled') state.datasets.set(...result.value);
    else errors.push(result.reason.message);
  });
  const completeWeeks = [...state.datasets.values()].map(dataset => dataset.completeWeek).filter(Boolean);
  const sharedCompleteWeek = completeWeeks.sort()[0];
  state.datasets.forEach(dataset => { dataset.sharedCompleteWeek = sharedCompleteWeek; });
  completeWeekNode.textContent = sharedCompleteWeek ?? '—';
  dashboard.setAttribute('aria-busy', 'false');
  statusNode.textContent = errors.length ? `部分数据读取失败：${errors.join('；')}` : '';
  render();
}

rangeButtons.forEach(button => button.addEventListener('click', () => {
  state.range = button.dataset.range;
  render();
}));


initialize().catch(error => {
  dashboard.setAttribute('aria-busy', 'false');
  statusNode.textContent = `数据读取失败：${error.message}`;
});
