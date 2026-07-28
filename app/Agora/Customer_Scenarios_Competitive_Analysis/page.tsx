import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "声网客户场景和竞争分析 | Agora Equity Research",
  description: "Agora 客户工作负载、买入与自建决策，以及客户迁入迁出的竞争分析。",
};

export default async function AgoraCustomerScenariosPage() {
  const zhPath = path.join(process.cwd(), "articles", "声网客户场景和竞争分析.md");
  const enPath = path.join(process.cwd(), "articles", "agora_customer_scenarios_and_competitive_analysis.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      enMarkdown={enMarkdown}
      enTitle="Agora Customer Scenarios and Competitive Analysis"
      zhMarkdown={zhMarkdown}
      zhTitle="声网客户场景和竞争分析"
    />
  );
}
