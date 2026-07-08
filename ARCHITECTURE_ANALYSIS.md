# Agora API Research — 架构与差异分析报告

> 生成日期: 2026-07-08 | 分析范围: 本地仓库 vs GitHub Remote (main 分支)

---

## 一、仓库概览

这是一个 **RTC 开发者生态下载量监控项目**，目标是通过 npm/PyPI 公开下载数据，持续追踪 Agora 及其竞争对手（LiveKit、Twilio、Bandwidth、腾讯 TRTC、ZEGO 等）在开发者侧的采用趋势。

核心能力：
- 从 npm downloads API 和 ClickPy (ClickHouse) 抓取原始下载数据
- 按周聚合生成 CSV 数据文件
- 生成交互式 HTML 看板（SVG 折线图 + 日期范围滑块）
- 输出 JSON metadata 用于自动化校验
- 通过 GitHub Pages 公开发布

---

## 二、本地库 vs GitHub Remote 差异

| 类别 | 文件数 (本地) | 文件数 (Remote) | 差异说明 |
|------|:-----------:|:-------------:|------|
| 根目录脚本 | 5 | 5 | 一致 |
| 共享 CSS/JS | 2 | 2 | 一致 |
| Data/ CSV | 7 | 7 | 一致 |
| html/ | 14 | 14 | 一致 (7主看板 + 7预览) |
| json/ | 5 | 5 | 一致 |
| Research_Report/ | 4 | 3 | **本地多1份** |
| Resources/ | 4 | 3 | **本地多1份** |
| generated_skills/ | 6 个 skill | 0 | **本地独有** |
| .gitignore | 无 | 无 | 都不存在 |

### 2.1 本地独有、未推送的文件

| 文件 | 状态 | 说明 |
|------|------|------|
| `Research_Report/rtc_voice_ai_agora_moat_report.md` | untracked | RTC 语音 AI 护城河研究报告 (~21KB)，从未提交 |
| `Resources/WebRTC 零基础开发者教程（中文）.pdf` | untracked | WebRTC 开发者教程 PDF (~3.9MB)，从未提交 |
| `base64_content.txt` | untracked | 二进制文件（可能为临时编码或缓存），从未提交 |
| `generated_skills/` (全部) | untracked | 6 个 Codex Agent 技能定义，从未提交 |

### 2.2 `generated_skills/` 目录分析

这是为自动化工作流准备的 Agent 技能包，每个 skill 定义一次看板更新流程。

| Skill 名称 | 脚本 | 说明 |
|------------|------|------|
| `agora-pypi-dashboard-update` | `build_pypi_dashboard_pages.py` | Agora PyPI 看板更新 |
| `agora-pypi-dashboard-updater` | `build_pypi_dashboard_pages.py` | **与上方重复！** 旧版 |
| `livekit-npm-dashboard-update` | `build_livekit_npm_dashboard.py` | LiveKit npm 看板更新 |
| `livekit-pypi-dashboard-update` | `build_livekit_pypi_dashboard.py` | LiveKit PyPI 看板更新 |
| `twilio-npm-dashboard-update` | `build_vendor_npm_dashboards.mjs` | Twilio npm 看板更新 |
| `bandwidth-npm-dashboard-update` | `build_vendor_npm_dashboards.mjs` | Bandwidth npm 看板更新 |

> ⚠️ `agora-pypi-dashboard-update` 和 `agora-pypi-dashboard-updater` 是**重复**的 skill，指向同一个脚本，内容高度相似，后者为旧版残留。

### 2.3 Remote 文件

Remote 和 Local 的 Data/html/json/脚本/根文件 **完全一致**，不存在 Remote 有而 Local 缺失的文件。Remote 缺少的只有上述 4 类本地独有文件。

---

## 三、架构分析

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      数据源 (External)                       │
│  npm Registry API  │  npm Downloads API  │  ClickPy/PyPI    │
└──────────────┬────────────────┬────────────────┬────────────┘
               │                │                │
    ┌──────────▼────┐  ┌───────▼────────┐  ┌───▼──────────────┐
    │ build_agora_  │  │ build_livekit_ │  │ build_pypi_      │
    │ npm_dashboard │  │ npm_dashboard  │  │ dashboard_pages  │
    │    .py (1293L)│  │   .py (825L)   │  │   .py (664L)     │
    └───────┬───────┘  └───────┬────────┘  └───┬──────────────┘
            │                  │                │
    ┌───────▼───────┐  ┌───────▼────────┐      │
    │ build_vendor_ │  │ build_livekit_ │      │
    │ npm_dashboards│  │ pypi_dashboard │      │
    │   .mjs (652L) │  │   .py (789L)   │      │
    └───────┬───────┘  └───────┬────────┘      │
            │                  │                │
            ▼                  ▼                ▼
    ┌───────────────────────────────────────────────────────────┐
    │                       输出产物                             │
    ├──────────────┬───────────────────┬────────────────────────┤
    │  Data/ (7)   │   html/ (14)      │    json/ (5)           │
    │  CSV 数据    │   HTML 看板       │    Metadata JSON       │
    └──────────────┴───────────────────┴────────────────────────┘
                                    │
                            ┌───────▼────────┐
                            │   index.html   │
                            │  (GitHub Pages  │
                            │   入口页面)     │
                            └────────────────┘
```

### 3.2 各文件/目录功能详解

#### 根目录脚本（5 个）

| 脚本 | 语言 | 行数 | 功能 | 数据源 |
|------|:----:|:----:|------|------|
| `build_agora_npm_dashboard.py` | Python | 1293 | Agora npm 9 个包的周度下载看板（含 AI 包分组） | npm Registry + Downloads API |
| `build_livekit_npm_dashboard.py` | Python | 825 | LiveKit npm 5 个包的周度下载看板 | npm Registry + Downloads API |
| `build_livekit_pypi_dashboard.py` | Python | 789 | LiveKit PyPI 4 个包的周度下载看板 | ClickPy ClickHouse + PyPI JSON API |
| `build_pypi_dashboard_pages.py` | Python | 664 | **共享模板引擎**：Agora + LiveKit PyPI 看板的 HTML 生成器 | 从 CSV 读取 |
| `build_vendor_npm_dashboards.mjs` | Node.js | 652 | Twilio (5包) + Bandwidth (3包) npm 看板 | npm Registry + Downloads API |

#### 共享前端资源（2 个）

| 文件 | 行数 | 功能 |
|------|:----:|------|
| `dashboard_range_controls.css` | 271 | 日期范围滑块（range brush）的样式，包含 DefiLlama 风格预览 |
| `dashboard_range_controls.js` | 400 | **共享图表控制器**：日期范围选择、刷选预览、hover tooltip、SVG 折线图渲染 |

> `dashboard_range_controls.js` 被所有看板引用，通过 `<script src="dashboard_range_controls.js">` 注入交互能力。它通过 `data-chart` 属性和 `data-series` JSON 数据实现通用图表渲染。

#### Data/ — CSV 数据层（7 个文件）

| CSV 文件 | 行范围 | 覆盖包数 | 说明 |
|----------|--------|:------:|------|
| `agora_npm_weekly_downloads.csv` | ~20KB | 9+1 派生列 | Agora 核心 SDK + AI Agent 包 |
| `agora_pypi_weekly_downloads.csv` | ~7.6KB | 4 | Agora Python 生态包 |
| `livekit_npm_weekly_downloads.csv` | ~8.7KB | 5 | LiveKit JS/TS 生态包 |
| `livekit_pypi_weekly_downloads.csv` | ~5.1KB | 4 | LiveKit Python 生态包 |
| `twilio_npm_weekly_downloads.csv` | ~19KB | 5 | Twilio 音视频包 |
| `bandwidth_npm_weekly_downloads.csv` | ~3.3KB | 3 | Bandwidth RTC 包 |
| `rtc_competitor_npm_weekly_downloads.csv` | ~7.4KB | 多包 | TRTC/ZEGO/阿里/火山等竞品 |

所有 CSV 均以 `week_start` 为第一列，周一为周起始日，保留最新不完整周。

#### html/ — 看板页面（14 个文件）

分为两类：
- **主看板**（7 个）：完整功能页面，含图表、滑块、元数据表
- **预览看板**（7 个，`*_preview.html`）：精简版，用于快速预览

| 主看板 | 大小 | 覆盖厂商 |
|--------|:----:|------|
| `agora_npm_downloads_dashboard.html` | 226KB | Agora |
| `agora_pypi_weekly_downloads_dashboard.html` | 155KB | Agora |
| `livekit_npm_downloads_dashboard.html` | 88KB | LiveKit |
| `livekit_pypi_downloads_dashboard.html` | 84KB | LiveKit |
| `twilio_npm_downloads_dashboard.html` | 141KB | Twilio |
| `bandwidth_npm_downloads_dashboard.html` | 41KB | Bandwidth |
| `rtc_competitor_npm_downloads_dashboard.html` | 125KB | 竞品汇总 |

#### json/ — 元数据层（5 个文件）

| JSON 文件 | 内容 |
|-----------|------|
| `agora_npm_downloads_metadata.json` | 数据源、包列表、派生列公式、图表策略 |
| `livekit_npm_downloads_metadata.json` | 同上（LiveKit npm） |
| `livekit_pypi_downloads_metadata.json` | 同上（LiveKit PyPI） |
| `twilio_npm_downloads_metadata.json` | 同上（Twilio） |
| `bandwidth_npm_downloads_metadata.json` | 同上（Bandwidth） |

> ⚠️ 缺少 `agora_pypi` 和 `rtc_competitor` 的 metadata JSON。

#### Research_Report/ — 研究报告（4 个）

| 报告 | 大小 | 主题 |
|------|:----:|------|
| `agora_rtc_technical_moat.md` | 17KB | Agora SD-RTN 技术护城河分析 |
| `OpenAI & LiveKit Relationship.md` | 38KB | OpenAI 与 LiveKit 合作关系深度分析 |
| `RTC工程细节深度报告.md` | 27KB | RTC 工程实现细节全面报告 |
| `rtc_voice_ai_agora_moat_report.md` *(未提交)* | 21KB | RTC 语音 AI 领域 Agora 护城河分析 |

#### Resources/ — 参考资料（4 个）

| 资源 | 大小 | 说明 |
|------|:----:|------|
| `Agora SD-RTN Introduction.jpg` | 316KB | SD-RTN 架构图 |
| `Agora_WP_SD-RTN-Delivers-RealTime-Internet-Advantages.pdf` | 7.7MB | 声网 SD-RTN 白皮书 |
| `Real-Time Communication with WebRTC.pdf` | 25MB | WebRTC 权威书籍 |
| `WebRTC 零基础开发者教程（中文）.pdf` *(未提交)* | 4MB | WebRTC 中文开发者教程 |

### 3.3 脚本间关系图

```
build_agora_npm_dashboard.py ─── 独立，自包含 HTML 生成
build_livekit_npm_dashboard.py ─── 独立，自包含 HTML 生成
build_livekit_pypi_dashboard.py ─── 依赖 → build_pypi_dashboard_pages.py (可选 fallback)
build_pypi_dashboard_pages.py ─── 共享的 PyPI 看板模板引擎
build_vendor_npm_dashboards.mjs ─── 独立，一个脚本服务 Twilio + Bandwidth 两个厂商
```

关键依赖关系：
- `build_livekit_pypi_dashboard.py` 会 `import build_pypi_dashboard_pages.build_page` 作为首选方案，失败时 fallback 到自带的 `build_html()` 方法
- `build_pypi_dashboard_pages.py` 中的 `build_page()` 是导出函数，被外部调用
- 所有 HTML 都引用 `<link rel="stylesheet" href="dashboard_range_controls.css">` 和 `<script src="dashboard_range_controls.js">`
- 部分脚本（Agora npm、Agora PyPI）内联了完整 JS 渲染代码作为 fallback/legacy

### 3.4 数据流

```
npm/PyPI API → Python/Node 脚本 → CSV (Data/)
                                 → HTML (html/) → GitHub Pages
                                 → JSON (json/)
```

每个脚本的执行流程：
1. fetch npm registry metadata（包名是否存在、创建日期等）
2. fetch npm downloads / ClickPy 日下载数据
3. 按周聚合（周一为起始日）
4. 写入 CSV（保留最新不完整周）
5. 生成 HTML（图表排除最新不完整周）
6. 生成 JSON metadata
7. 输出结果摘要到 stdout

---

## 四、架构问题与改进建议

### 4.1 架构层面

#### 问题 1：脚本职责过重，单体化严重
每个脚本同时承担数据获取 → CSV 写入 → HTML 生成 → JSON 输出 → 内联 CSS/JS，单个文件最高 1293 行。LiveKit npm 和 Agora npm 两个 Python 脚本有大量重复代码（`fetch_json`、`week_start`、`nice_y_max`、`compact_int`、`interactive_chart_shell` 等）。

**建议**：抽取公共 Python 模块 `lib/npm_utils.py` 和 `lib/chart_utils.py`，将 fetch/聚合/图表渲染逻辑集中管理。

#### 问题 2：双语言混用增加维护成本
npm 看板使用 Python（Agora、LiveKit）和 Node.js（Twilio、Bandwidth）两种语言。`build_vendor_npm_dashboards.mjs` 中的逻辑与 Python 脚本高度相似但独立实现。

**建议**：统一到一种语言。考虑到项目整体以 Python 为主（4/5 脚本），建议将 `build_vendor_npm_dashboards.mjs` 迁移到 Python，复用公共库。

#### 问题 3：HTML/CSS/JS 分散重复
- 每个脚本的 `build_html()` 函数都包含 ~200 行内联 CSS，大量重复（字体、颜色变量、布局）。
- SVG 图表渲染 JS 在 5 个脚本中各实现了一遍，仅在细微处有差异（tooltip 样式、Y 轴算法）。
- `dashboard_range_controls.js` 出现后，部分脚本仍保留了自带的 fallback JS 渲染。

**建议**：
- 抽取共享 CSS 为 `styles/dashboard.css`，脚本只生成 `<link>` 标签
- 将图表 JS 渲染完全收敛到 `dashboard_range_controls.js`，移除脚本中的内联 JS
- 统一 Y 轴刻度算法（目前不同脚本使用了略有不同的 `niceYMax` 实现）

#### 问题 4：generated_skills 目录未纳入版本管理
`generated_skills/` 定义了 6 个自动化 Workflow Skill（含重复的 `agora-pypi-dashboard-updater`），但从未提交到 Git。

**建议**：
- 清理重复的 `agora-pypi-dashboard-updater`（保留 `agora-pypi-dashboard-update`）
- 将 `generated_skills/` 提交到仓库（或移到 `.github/` / `automation/` 目录）
- 这些 skill 定义与 `workflow.md` 之间有重叠，建议 skill 只定义自动化触发规则，具体步骤引用 `workflow.md`

#### 问题 5：缺少自动化 CI/CD
当前工作流依赖手动运行脚本或手动触发 Agent。没有 GitHub Actions 做定时抓取、校验、自动提交。

**建议**：添加 GitHub Actions workflow，每周自动运行更新脚本，生成 CSV/HTML/JSON 并自动提交（或创建 PR）。

### 4.2 工作流层面

#### 问题 6：workflow.md 冗长且包含实现细节
`workflow.md`（132 行）混合了目标声明、工具清单、skill 映射和执行步骤。skill 定义（位于 `generated_skills/`）与 workflow.md 有大量重复。

**建议**：
- `workflow.md` 保留目标、规则和失败处理
- 每个 skill 的 `SKILL.md` 只保留该 skill 特有的包列表和输出路径
- 公共步骤（校验、归档、Git 操作）引用 `workflow.md`

#### 问题 7：部分 metadata JSON 缺失
Agora PyPI 和 RTC competitor 看板有 HTML 和 CSV 但没有对应的 metadata JSON。不符合 `workflow.md` 中的校验要求。

**建议**：补充 `agora_pypi_downloads_metadata.json` 和 `rtc_competitor_npm_downloads_metadata.json`。

#### 问题 8：base64_content.txt 垃圾文件
项目根目录有一个未追踪的二进制/缓存文件，无实际用途。

**建议**：删除或加入 `.gitignore`。

#### 问题 9：缺少 .gitignore
项目完全没有 `.gitignore` 文件。

**建议**：创建 `.gitignore`，忽略 `__pycache__/`、`*.pyc`、`node_modules/`、`.workbuddy/` 等。

#### 问题 10：预览看板 (*_preview.html) 的管理策略不清晰
html/ 目录下有 7 个预览看板，与主看板并列存放，没有明确区分。

**建议**：如果预览看板是自动化生成的中间产物，放入 `html/preview/` 子目录；如果是手动生成的分析变体，加注释说明生成条件和用途。

### 4.3 建议的目录结构

```
Agora_API_Research/
├── .github/
│   └── workflows/
│       └── weekly-dashboard-update.yml   # 每周自动更新
├── .gitignore
├── README.md
├── index.html                             # GitHub Pages 入口
├── workflow.md                            # 工作流总体规范
├── lib/
│   ├── npm_utils.py                       # 公共 npm fetch/聚合
│   └── chart_utils.py                     # 公共图表生成
├── scripts/
│   ├── build_agora_npm.py
│   ├── build_livekit_npm.py
│   ├── build_livekit_pypi.py
│   ├── build_pypi_dashboards.py
│   └── build_vendor_npm.py               # Twilio + Bandwidth (迁移到 Python)
├── styles/
│   └── dashboard.css                      # 共享 CSS
├── js/
│   └── dashboard_range_controls.js
├── Data/                                  # CSV 数据
├── html/                                  # 主看板 HTML
│   └── preview/                           # 预览看板（可选）
├── json/                                  # Metadata JSON
├── Research_Report/                       # 研究报告
├── Resources/                             # 参考资料
└── automation/                            # Agent 技能定义
    ├── agora-pypi-dashboard-update/
    ├── livekit-npm-dashboard-update/
    ├── livekit-pypi-dashboard-update/
    ├── twilio-npm-dashboard-update/
    └── bandwidth-npm-dashboard-update/
```

---

## 五、总结

| 维度 | 现状 | 评分 |
|------|------|:--:|
| 功能完整性 | 覆盖 5 个厂商、npm+PyPI 双生态、7 个看板 | ★★★★★ |
| 数据质量 | 有校验规则、metadata、图表排除不完整周 | ★★★★☆ |
| 代码复用 | 大量重复代码，5 个脚本独立实现图表渲染 | ★★☆☆☆ |
| 自动化程度 | 依赖手动触发，无 CI/CD | ★★☆☆☆ |
| 文档完整性 | README + workflow.md + Research_Report 齐全 | ★★★★☆ |
| 版本管理 | 4 类本地文件未提交，无 .gitignore | ★★★☆☆ |
