# 单页看板更新流程

## 目标

每周刷新首页使用的六个数据集。更新任务只生成：

- `Data/*.csv`
- `json/*.json`

`index.html`、`css/home.css` 和 `scripts/home.js` 是唯一页面层，不生成独立 HTML 子页面。

## 更新入口

| 数据集 | 命令 |
|---|---|
| Agora npm | `python scripts/build_agora_npm_dashboard.py` |
| Agora PyPI | `python scripts/build_agora_pypi_dashboard.py` |
| LiveKit npm | `python scripts/build_livekit_npm_dashboard.py` |
| LiveKit PyPI | `python scripts/build_livekit_pypi_dashboard.py` |
| Twilio npm | `python scripts/build_vendor_npm_dashboards.py` |
| 腾讯 TRTC npm | `python scripts/build_rtc_competitor_dashboard.py` |

## 执行步骤

1. 运行 `git status -sb`，记录并保留已有用户改动。
2. 运行需要更新的数据脚本。网络失败时重试，不手工填写下载量。
3. 检查 CSV：
   - 第一列为 `week_start`；
   - 日期为周一的 ISO 日期；
   - 其余列与首页包名一致；
   - 周次连续，数值为非负整数或空值。
4. 检查 metadata：
   - 包含数据来源和生成时间；
   - 包含 `source.latest_complete_week_start`；
   - `dataset.columns` 与 CSV header 一致。
5. 本地启动静态服务器并打开根目录页面，确认 17 张图均可加载，时间范围和深浅色切换正常。
6. 用 `git diff --stat` 和 `git diff --check` 检查变更，只提交本次更新的数据集。
7. 用户要求发布时再提交、推送，并验证 GitHub Pages 根页面。

## 完整周规则

CSV 可以保留最新未完整周；首页以六个数据集共同可用的最近完整周为截止日。不得用部分周数据计算最新值或同比。

## 保留范围

`Research_Report/` 和 `Resources/` 为长期资料区，不属于每周数据更新的清理范围。
