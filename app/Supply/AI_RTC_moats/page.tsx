import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "AI 对 RTC 业务护城河的影响 | Agora Equity Research",
  description: "AI 对 RTC 业务护城河与行业供给难度的影响分析。",
};

export default async function AIRTCMoatsPage() {
  const zhPath = path.join(process.cwd(), "articles", "AI对RTC业务护城河的影响.md");
  const enPath = path.join(process.cwd(), "articles", "Impact_of_AI_on_RTC_Business_Moats.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      enMarkdown={enMarkdown}
      enTitle="Impact of AI on RTC Business Moats"
      zhMarkdown={zhMarkdown}
      zhTitle="AI对RTC业务护城河的影响"
    />
  );
}