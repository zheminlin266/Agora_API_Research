# Agora Research

Agora Research 是一个面向实时互动行业的双语研究网站，围绕行业需求、行业供给与声网竞争优势组织长期研究和公开数据。

- 网站：[agora.zhemin.ltd](https://agora.zhemin.ltd/)
- 开发者下载看板：[RTC Dev npm downloads](https://agora.zhemin.ltd/Demand/Dev_npm_downloads/)

## 网站结构

| 路径 | 内容 |
|---|---|
| `/` | Agora Research 首页与研究框架 |
| `/Demand/Dev_npm_downloads/` | Agora、LiveKit、Twilio 和腾讯 RTC 的 17 个 npm / PyPI 包周度下载趋势 |

两页共用顶部导航、中英文切换和明暗主题。语言及主题偏好保存在浏览器本地存储中，并在页面之间保持一致。

## 技术结构

```text
app/
├─ page.tsx                              # 首页路由
├─ layout.tsx                            # 全局 metadata 与偏好 Provider
└─ Demand/Dev_npm_downloads/             # 开发者下载看板路由
components/
├─ site-header.tsx                       # 全站共享顶部功能行
├─ site-preferences.tsx                  # 语言与主题状态
├─ home-page.tsx                         # 首页内容
└─ download-dashboard.tsx                # 双语数据看板与 SVG 图表
public/data/dev-npm-downloads/
├─ Data/                                 # 六个周度 CSV 数据集
└─ json/                                 # 数据来源与完整周 metadata
scripts/                                 # 数据更新入口
lib/                                     # npm / PyPI 抓取与周度聚合
Research_Report/                         # 研究报告
Resources/                               # 研究资料
```

网站采用 Next.js 16 App Router、React 19 和 TypeScript。图表使用原生 SVG 绘制，不依赖第三方图表库。

## 本地预览

```powershell
npm install
npm run dev
```

打开 `http://127.0.0.1:3000/`。生产构建检查：

```powershell
npm run typecheck
npm run build
npm run start
```

## 数据更新

按数据集运行对应脚本：

```powershell
python scripts/build_agora_npm_dashboard.py
python scripts/build_agora_pypi_dashboard.py
python scripts/build_livekit_npm_dashboard.py
python scripts/build_livekit_pypi_dashboard.py
python scripts/build_vendor_npm_dashboards.py
python scripts/build_rtc_competitor_dashboard.py
```

脚本直接更新 `public/data/dev-npm-downloads/`。详细校验与发布流程见 [workflow.md](workflow.md)。

## 数据口径

npm 数据来自官方 Downloads API；PyPI 数据来自 ClickPy 公共 ClickHouse 数据集。页面以六个数据集共同可用的最近完整周为截止日。

下载量包含自动化安装、CI、镜像、缓存和依赖安装等影响，只适合观察单个软件包的方向与持续性，不等同于客户数、应用数或商业收入。

## 部署

`main` 分支连接 Vercel 项目 `agora-research`，生产域名为 `agora.zhemin.ltd`。推送到 `main` 后会自动触发生产部署。
