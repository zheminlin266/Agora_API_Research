# Scheduled Dashboard Update Workflow

## 目标

这个项目维护 Agora API 研究相关的数据看板。scheduled 更新任务需要定期刷新 npm/PyPI 下载量数据，重新生成看板文件，并按类型归档：

- `Data/`: CSV 数据文件。
- `html/`: HTML 看板页面。根目录入口 `index.html` 例外，必须保留在项目根目录，以维持 GitHub Pages 入口。
- `json/`: metadata JSON 文件。

本次整理规则：项目根目录下已有的 `.csv` 和 `.json` 文件已经分别移动到 `Data/` 和 `json/`；看板 `.html` 文件移动到 `html/`，但根目录入口 `index.html` 保留在项目根目录。

## Scheduled 计划

- 建议频率：每周一次，在 npm 或 PyPI 最新完整周数据可用后运行。
- 运行入口：scheduled 自动唤醒 Codex，并说明要更新哪个看板。
- 执行原则：数据抓取、CSV 生成、HTML 生成、JSON 生成、校验、提交和推送都在 Codex 中完成。
- 发布原则：GitHub Pages 只用于推送后的只读验证，不作为数据生成步骤。

## 工具

- PowerShell：检查目录、移动文件、读取产物、做轻量校验。
- Git：检查工作区、查看 diff、只提交本次相关文件、推送到 `origin main`。
- Python：运行 Python dashboard 更新脚本。
- Node.js：运行共享 npm vendor dashboard 更新脚本。
- npm registry/downloads API：获取 npm 包元数据和下载量。
- PyPI/BigQuery 或既有脚本数据源：按现有 PyPI 脚本逻辑刷新 PyPI 下载量。
- GitHub Pages HTTP 验证：确认公开页面返回 HTTP 200，并包含关键包名、标题和最新完整周标记。
- Browser Use skill：默认不用。只有在需要浏览器自动化、登录态、表单操作、网页交互抽取或重复浏览器流程时才使用。

## Skills

按本次看板选择最小必要 skill，不要混用无关 skill。

- `agora-npm-dashboard-update`
  - 用于 Agora npm 周度下载 CSV、HTML dashboard、metadata JSON。
  - 脚本：`build_agora_npm_dashboard.py`。
  - 输出：`agora_npm_weekly_downloads.csv`、`agora_npm_downloads_dashboard.html`、`agora_npm_downloads_metadata.json`。
  - 关键逻辑：`rtc-sdk-total = agora-rtc-sdk-ng + agora-rtc-sdk`；CSV 可保留最新不完整周；HTML 图表排除最新不完整周；HTML 需要包含 AI related 区块。

- `twilio-npm-dashboard-update`
  - 用于 Twilio npm 周度下载 CSV、HTML dashboard、metadata JSON。
  - 脚本：`build_vendor_npm_dashboards.mjs`。
  - 输出：`twilio_npm_weekly_downloads.csv`、`twilio_npm_downloads_dashboard.html`、`twilio_npm_downloads_metadata.json`。
  - 关键逻辑：脚本会同时刷新 Twilio 和 Bandwidth；如果只提交 Twilio，需要只 stage Twilio 相关文件。

- `bandwidth-npm-dashboard-update`
  - 用于 Bandwidth npm 周度下载 CSV、HTML dashboard、metadata JSON。
  - 脚本：`build_vendor_npm_dashboards.mjs`。
  - 输出：`bandwidth_npm_weekly_downloads.csv`、`bandwidth_npm_downloads_dashboard.html`、`bandwidth_npm_downloads_metadata.json`。
  - 关键逻辑：脚本会同时刷新 Twilio 和 Bandwidth；如果只提交 Bandwidth，需要只 stage Bandwidth 相关文件。

- `livekit-npm-dashboard-update`
  - 用于 LiveKit npm 周度下载 CSV、HTML dashboard、metadata JSON。
  - 脚本：`build_livekit_npm_dashboard.py`。
  - 输出：`livekit_npm_weekly_downloads.csv`、`livekit_npm_downloads_dashboard.html`、`livekit_npm_downloads_metadata.json`。
  - 关键逻辑：metadata 需要说明 HTML 图表排除最新不完整周，CSV 保留所有周度聚合。

- `agora-pypi-dashboard-update` 或 `agora-pypi-dashboard-updater`
  - 用于 Agora PyPI 周度下载 CSV 和 HTML dashboard。
  - 脚本：`build_pypi_dashboard_pages.py`。
  - 输出：`agora_pypi_weekly_downloads.csv`、`agora_pypi_weekly_downloads_dashboard.html`。

- `livekit-pypi-dashboard-update`
  - 用于 LiveKit PyPI 周度下载 CSV、HTML dashboard、metadata JSON。
  - 脚本：`build_livekit_pypi_dashboard.py`。
  - 输出：`livekit_pypi_weekly_downloads.csv`、`livekit_pypi_downloads_dashboard.html`、`livekit_pypi_downloads_metadata.json`。

## 执行步骤

1. 确认范围
   - 从 scheduled 请求中确认 vendor 和生态：Agora/Twilio/Bandwidth/LiveKit，npm/PyPI，或 competitor 汇总页。
   - 只选择对应 skill 和脚本。

2. 检查工作区
   - 在项目根目录运行 `git status -sb`。
   - 记录已有未提交改动。
   - 不要回滚、覆盖或提交无关用户改动。

3. 运行更新脚本
   - Agora npm：`python build_agora_npm_dashboard.py`。
   - Twilio/Bandwidth npm：`node "build_vendor_npm_dashboards.mjs"`。
   - Twilio/Bandwidth 只重建页面：`node "build_vendor_npm_dashboards.mjs" --from-existing`。
   - LiveKit npm：`python build_livekit_npm_dashboard.py`。
   - Agora PyPI：`python build_pypi_dashboard_pages.py`。
   - LiveKit PyPI：`python build_livekit_pypi_dashboard.py`。
   - 网络失败时，按 Codex 权限流程请求 sandbox escalation 后重试同一命令。

4. 数据和图表逻辑
   - CSV 保存原始周度聚合结果，不手工删行。
   - HTML 折线图只展示完整周，排除最新不完整周。
   - JSON metadata 写清楚 `latest_download_day`、`html_chart_complete_through_week_start` 和 `html_chart_policy`。
   - 派生列必须可复算，不能手工填一个无法追溯的数字。

5. 校验输出
   - CSV header 与对应 skill 说明一致。
   - HTML 包含 vendor 标题、全部包名、`range-start`、`range-end` 和最新完整周标记。
   - JSON 包含源日期、完整周、图表策略。
   - 对汇总页，确认所有子看板链接仍然指向正确位置。

6. 按类型归档
   - `.csv` 放入 `Data/`。
   - 看板 `.html` 放入 `html/`，但根目录入口 `index.html` 保留在项目根目录。
   - `.json` 放入 `json/`。
   - 如果脚本仍在根目录生成文件，更新完成后再次执行归档步骤。
   - GitHub Pages 入口 `index.html` 必须保留在项目根目录；不要把它归档进 `html/`。

7. 检查 diff
   - 运行 `git diff --stat`。
   - 只 stage 本次范围内的 CSV/HTML/JSON 和必要脚本改动。
   - 如果共享脚本产生了多个 vendor 变化，而本次只要求一个 vendor，其他 vendor 文件保持 unstaged，除非用户明确要求一起发布。

8. 提交和推送
   - 只有存在实际变更时才提交。
   - commit message 示例：`Update Agora npm dashboard`。
   - 推送到 `origin main`。

9. 公开页面验证
   - 请求 GitHub Pages URL，确认 HTTP 200。
   - 页面内容应包含标题、关键包名和最新完整周标记。
   - 如果 Pages 缓存延迟，报告 commit hash、HTTP 状态、`Last-Modified` 和 GitHub main 分支文件证据，不要触发 GitHub Actions 重跑。

## 失败处理

- 网络失败：申请 escalation 后重跑，不手写下载量。
- header 不匹配：停止发布，检查脚本包列表或 schema。
- HTML 图表包含最新不完整周：停止发布，修正过滤逻辑。
- metadata 缺字段：停止发布，补齐 JSON 生成逻辑。
- Git 工作区有无关改动：保留并报告，不纳入本次提交。
- 移动文件后链接失效：更新 `index.html`、README 或 Pages 路径，直到入口可访问。

## 最小自检

- `Data/`、`html/`、`json/` 存在。
- CSV 和 JSON 都在对应目录；看板 HTML 在 `html/`，根目录入口 `index.html` 留在项目根目录。
- 根目录保留脚本、README、样式、JS 等非数据产物。
- 对应 skill 的 CSV/HTML/JSON 校验全部通过。
- `git status -sb` 只显示预期变更和已知无关改动。
- GitHub Pages 或本地入口链接没有因移动文件而断掉。