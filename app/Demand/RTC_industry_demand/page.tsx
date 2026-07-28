import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "RTC 行业需求 | Agora Equity Research",
  description: "RTC 行业需求场景、participant-minutes 规模与历史变化。",
};

export default async function RTCIndustryDemandPage() {
  const zhPath = path.join(process.cwd(), "articles", "RTC行业需求.md");
  const enPath = path.join(process.cwd(), "articles", "RTC Industry Demand.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      enMarkdown={enMarkdown}
      enTitle="RTC Industry Demand"
      zhMarkdown={zhMarkdown}
      zhTitle="RTC行业需求"
    />
  );
}