# RTC 开发者下载看板更新流程

## 目标

刷新 `/Demand/Dev_npm_downloads/` 使用的六个周度数据集：

- `public/data/dev-npm-downloads/Data/*.csv`
- `public/data/dev-npm-downloads/json/*.json`

页面层由 `app/Demand/Dev_npm_downloads/` 和 `components/download-dashboard.tsx` 维护。数据更新任务不生成 HTML、CSS 或 JavaScript 文件。

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
5. 运行 `npm run typecheck` 和 `npm run build`。
6. 启动生产预览并检查：
   - `/` 与 `/Demand/Dev_npm_downloads/` 均返回 200；
   - 17 张图表全部加载；
   - 中英文和明暗主题切换正常；
   - 时间范围切换正常；
   - 浏览器控制台无错误。
7. 用 `git diff --stat` 和 `git diff --check` 检查变更，只提交本次数据文件。
8. 用户要求发布时再推送，并在 `https://agora.zhemin.ltd/Demand/Dev_npm_downloads/` 验证生产页面。

## 完整周规则

CSV 可以保留最新未完整周；页面以六个数据集共同可用的最近完整周为截止日。不得用部分周数据计算最新值或同比。

## 保留范围

`Research_Report/` 和 `Resources/` 为长期资料区，不属于每周数据更新的清理范围。
