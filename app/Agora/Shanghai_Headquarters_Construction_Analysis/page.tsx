import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "上海总部建设分析 | Agora Equity Research",
  description: "声网上海总部项目的土地成本、建设支出、潜在租金回报与项目融资条款分析。",
};

export default async function ShanghaiHeadquartersConstructionAnalysisPage() {
  const zhPath = path.join(process.cwd(), "articles", "上海总部建设分析.md");
  const enPath = path.join(process.cwd(), "articles", "Shanghai_Headquarters_Construction_Analysis_EN.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      articleClassName="shanghai-headquarters-analysis"
      enMarkdown={enMarkdown}
      enTitle="Shanghai Headquarters Construction Analysis"
      zhMarkdown={zhMarkdown}
      zhTitle="上海总部建设分析"
    />
  );
}
