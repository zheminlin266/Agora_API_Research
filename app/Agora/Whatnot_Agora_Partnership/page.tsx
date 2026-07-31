import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "Whatnot 与 Agora 直播合作 | Agora Equity Research",
  description: "Whatnot 与 Agora 在超大规模实时直播中的合作案例。",
};

export default async function WhatnotAgoraPartnershipPage() {
  const zhPath = path.join(process.cwd(), "articles", "Whatnot & Agora直播合作.md");
  const enPath = path.join(process.cwd(), "articles", "Whatnot & Agora Livestream Partnership.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      enMarkdown={enMarkdown}
      enTitle="Whatnot & Agora Livestream Partnership"
      zhMarkdown={zhMarkdown}
      zhTitle="Whatnot & Agora直播合作案例"
    />
  );
}