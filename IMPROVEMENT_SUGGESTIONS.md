# 改进建议：代码复用、自动化、版本管理

> 生成日期: 2026-07-08 | 基于本次重构经验

---

## 一、已完成的改进

### 1.1 共享库抽取 (lib/npm_dashboard.py)

**改动前**：3 个 npm 脚本各自独立实现 fetch_json、PackageMeta、load_package_meta、load_daily_downloads、weekly_from_daily、build_csv_rows、interactive_chart_shell、interactive_dashboard_script 等约 20 个函数，总计约 2770 行重复代码。

**改动后**：

| 文件 | 改动前 | 改动后 | 变化 |
|------|:------:|:------:|:----:|
| build_agora_npm_dashboard.py | 1293 | 111 | -91% |
| build_livekit_npm_dashboard.py | 825 | 75 | -91% |
| build_vendor_npm_dashboards.mjs → .py | 652 | 113 | -83% |
| lib/npm_dashboard.py (新增) | — | 707 | — |
| **合计** | **2770** | **1006** | **-64%** |

每个 vendor 脚本现在只需定义配置（包列表、颜色、注释、分段）并调用 `run(config)`。

### 1.2 语言统一

`build_vendor_npm_dashboards.mjs` (Node.js) 已迁移为 `build_vendor_npm_dashboards.py` (Python)，复用 `lib/npm_dashboard.py` 共享库。项目不再依赖 Node.js 运行时。

### 1.3 版本管理优化

- 创建 `.gitignore`（Python/Node/IDE/OS/WorkBuddy 临时文件）
- 清理 `base64_content.txt` 垃圾文件
- 删除重复的 `agora-pypi-dashboard-updater` skill
- 研究报告、资源文件、skills 全部推送到 GitHub

---

## 二、后续建议

### 2.1 代码复用

#### 建议 A：PyPI 脚本也抽取共享库

当前 `build_livekit_pypi_dashboard.py` 和 `build_pypi_dashboard_pages.py` 的 ClickHouse 查询、PyPI metadata 获取逻辑仍然独立。建议创建 `lib/pypi_dashboard.py`，提取：
- `fetch_url` / `fetch_json` / `clickhouse_csv`（HTTP + ClickHouse 查询）
- `load_package_meta`（PyPI JSON API 元数据获取）
- `latest_download_day`（ClickHouse 最新日期查询）
- `fetch_weekly_downloads`（周度下载量聚合查询）

**优先级**：中。当前只有 2 个 PyPI 脚本，重复量低于 npm 侧。

#### 建议 B：HTML 模板进一步统一

当前 `lib/npm_dashboard.py` 的 `build_html` 已统一了 npm 侧的 HTML 生成。但 PyPI 侧的 HTML 由 `build_pypi_dashboard_pages.py` 独立生成，样式和布局与 npm 侧有细微差异。

建议：将 PyPI 看板的 HTML 生成也接入 `lib/npm_dashboard.py` 的 `build_html`，或创建一个更通用的 `lib/dashboard_html.py` 统一所有看板的 HTML 模板。

**优先级**：低。功能正常，差异仅是视觉细节。

#### 建议 C：RTC competitor 看板接入共享库

`rtc_competitor_npm_downloads_dashboard.html` 存在于 html/ 目录，但没有对应的构建脚本在仓库中。如果它是手动生成的，建议创建一个 `build_rtc_competitor_dashboard.py` 配置文件，接入共享库自动生成。

**优先级**：中。当前该看板无法自动更新。

### 2.2 自动化

#### 建议 D：添加 GitHub Actions 定时更新

当前工作流完全依赖手动触发或 Agent 唤醒。建议添加 `.github/workflows/weekly-dashboard-update.yml`：

```yaml
name: Weekly Dashboard Update
on:
  schedule:
    - cron: '0 3 * * 1'  # 每周一 UTC 3:00
  workflow_dispatch:       # 手动触发
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python build_agora_npm_dashboard.py
      - run: python build_livekit_npm_dashboard.py
      - run: python build_vendor_npm_dashboards.py
      - run: python build_livekit_pypi_dashboard.py
      - run: python build_pypi_dashboard_pages.py
      - run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add Data/ html/ json/
          git diff --staged --quiet || git commit -m "Weekly dashboard update"
          git push
```

**优先级**：高。这是提升自动化程度最有效的改进。

#### 建议 E：补充缺失的 metadata JSON

当前缺少：
- `json/agora_pypi_downloads_metadata.json`
- `json/rtc_competitor_npm_downloads_metadata.json`

建议在对应的构建脚本中添加 `write_metadata` 调用。

**优先级**：中。影响自动化校验流程。

#### 建议 F：脚本输出路径直接写入目标目录

当前脚本在根目录生成文件，然后 workflow.md 要求手动移动到 `Data/`、`html/`、`json/`。建议脚本直接写入目标目录，消除移动步骤和相关的路径断链风险。

同时需要修复 CSS/JS 引用路径：当 HTML 在 `html/` 目录时，`<link href="dashboard_range_controls.css">` 会 404，应改为 `<link href="../dashboard_range_controls.css">`。

**优先级**：高。当前路径问题是潜在 bug。

### 2.3 版本管理

#### 建议 G：预览看板管理策略

`html/` 目录下有 7 个 `*_preview.html` 文件，与主看板并列存放。建议：
- 如果是自动化生成的中间产物 → 移入 `html/preview/` 子目录或加入 `.gitignore`
- 如果是手动分析变体 → 在 README 或 workflow.md 中说明生成条件和用途

**优先级**：低。不影响功能。

#### 建议 H：CSV BOM 统一

原 `build_vendor_npm_dashboards.mjs` 写入 UTF-8 BOM (`\ufeff`)，而 Python 脚本不写 BOM。建议统一为不写 BOM（UTF-8 without BOM 是更通用的标准），或在所有脚本中统一写入。

**优先级**：低。对 Excel 打开 CSV 有轻微影响。

#### 建议 I：添加 requirements.txt 或 pyproject.toml

当前项目没有声明 Python 依赖。虽然所有脚本都只用标准库（`urllib`、`csv`、`json` 等），但建议添加一个 `pyproject.toml` 声明 Python 版本要求，方便 CI 和新贡献者快速上手。

**优先级**：低。当前无第三方依赖。

---

## 三、改进优先级总结

| 优先级 | 建议 | 预期收益 |
|:------:|------|------|
| 高 | D: GitHub Actions 定时更新 | 完全自动化，不再需要手动触发 |
| 高 | F: 脚本直接写入目标目录 | 消除移动步骤，修复 CSS/JS 路径 bug |
| 中 | A: PyPI 共享库 | 减少 PyPI 脚本重复代码 |
| 中 | C: RTC competitor 看板接入 | 所有看板可自动更新 |
| 中 | E: 补充缺失 metadata JSON | 完善自动化校验 |
| 低 | B: HTML 模板统一 | 视觉一致性 |
| 低 | G: 预览看板管理 | 目录整洁 |
| 低 | H: CSV BOM 统一 | 跨平台一致性 |
| 低 | I: 添加 pyproject.toml | 项目规范化 |
