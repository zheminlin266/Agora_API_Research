# Agora API Research

这是一个单页 RTC 开发者生态看板，汇总 Agora、LiveKit、Twilio 和腾讯 RTC 共 17 个 npm/PyPI 包的周度下载趋势。

## 页面

GitHub Pages 入口：`index.html`。页面直接读取 `Data/` 中的 CSV 和 `json/` 中的 metadata，不再生成或链接独立子页面。

## 目录

- `index.html`：单页入口。
- `css/home.css`：页面样式。
- `scripts/home.js`：数据加载、时间范围、指标和图表渲染。
- `scripts/build_*.py`：六个数据更新入口。
- `lib/`：npm/PyPI 抓取、周度聚合和 metadata 生成。
- `Data/`：六个周度数据集。
- `json/`：六个数据集的来源与完整周信息。
- `Research_Report/`：研究报告，长期保留。
- `Resources/`：研究资料与音视频技术资料，长期保留。
- `generated_skills/`：相关数据更新任务的本地技能说明。

## 数据更新

```powershell
python scripts/build_agora_npm_dashboard.py
python scripts/build_agora_pypi_dashboard.py
python scripts/build_livekit_npm_dashboard.py
python scripts/build_livekit_pypi_dashboard.py
python scripts/build_vendor_npm_dashboards.py
python scripts/build_rtc_competitor_dashboard.py
```

脚本只更新对应的 CSV 和 metadata。详细校验步骤见 `workflow.md`。

## 数据口径

npm 数据来自 npm Downloads API；PyPI 数据来自 ClickPy 公共 ClickHouse 数据集。下载量包含自动化安装、CI、镜像和缓存等影响，只适合观察生态趋势，不等同于客户数、应用数或收入。
