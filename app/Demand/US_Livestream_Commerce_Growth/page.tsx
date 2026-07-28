import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "美国直播电商增长情况 | Agora Equity Research",
  description: "美国直播电商市场、Whatnot 与 TikTok Shop/Live 的增长情况。",
};

export default async function USLivestreamCommerceGrowthPage() {
  const zhPath = path.join(process.cwd(), "articles", "美国直播电商增长情况.md");
  const enPath = path.join(process.cwd(), "articles", "U.S. Livestream Commerce Growth.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      enMarkdown={enMarkdown}
      enTitle="U.S. Livestream Commerce Growth"
      zhMarkdown={zhMarkdown}
      zhTitle="美国直播电商增长情况"
    />
  );
}
