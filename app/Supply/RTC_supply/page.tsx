import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "RTC 行业供给 | Agora Equity Research",
  description: "RTC 行业供给格局、进入与退出案例，以及 AI 对供给难度的影响。",
};

export default async function SupplyArticlePage() {
  const articlePath = path.join(process.cwd(), "articles", "RTC行业供给.md");
  const englishArticlePath = path.join(process.cwd(), "articles", "RTC_industry_supply.en.md");
  const [markdown, englishMarkdown] = await Promise.all([
    readFile(articlePath, "utf8"),
    readFile(englishArticlePath, "utf8"),
  ]);

  return <LocalizedMarkdownArticle enMarkdown={englishMarkdown} zhMarkdown={markdown} />;
}
