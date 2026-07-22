# Agora Research

Agora Research 是一个基于 Next.js App Router 的实时互动行业研究首页，聚焦行业需求、行业供给与声网竞争优势。

## 本地预览

```powershell
npm install
npm run dev
```

默认地址：`http://127.0.0.1:3000`

## 前端结构

- `app/page.tsx`：首页入口。
- `app/layout.tsx`：页面 metadata、主题预初始化与全局布局。
- `app/globals.css`：760px 正文版式、字体、主题、导航下拉及响应式样式。
- `components/agora-home.tsx`：页头、双语切换、明暗主题与首页内容。
- `assets/Agora_Logo.png`：页头使用的 Agora 品牌图标。

项目根目录原有的 `index.html`、`css/home.css` 与 `scripts/home.js` 仍作为历史 RTC 开发者生态看板代码保留；Next.js 首页不依赖这些文件。

## 研究数据与更新脚本

- `scripts/build_*.py`：npm / PyPI 数据更新入口。
- `lib/`：npm / PyPI 抓取、周度聚合和 metadata 生成。
- `Data/`：六个周度数据集。
- `json/`：数据来源与完整周信息。
- `Research_Report/`：研究报告。
- `Resources/`：研究资料与音视频技术资料。

npm 数据来自 npm Downloads API；PyPI 数据来自 ClickPy 公共 ClickHouse 数据集。下载量只适合观察生态趋势，不等同于客户数、应用数或收入。
