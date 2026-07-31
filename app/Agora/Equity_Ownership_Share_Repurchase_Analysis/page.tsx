import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "股权结构与回购分析 | Agora Equity Research",
  description: "声网股权结构、主要股东、股份回购与潜在卖压来源分析。",
};

export default async function AgoraEquityOwnershipPage() {
  const zhPath = path.join(process.cwd(), "articles", "股权结构与回购分析.md");
  const enPath = path.join(process.cwd(), "articles", "Equity Ownership and Share Repurchase Analysis.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      enMarkdown={enMarkdown}
      enTitle="Equity Ownership and Share Repurchase Analysis"
      zhMarkdown={zhMarkdown}
      zhTitle="股权结构与回购分析"
    />
  );
}
