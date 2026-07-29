import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "AI语音对基础设施需求的特性 | Agora Equity Research",
  description: "AI语音与直播电商、社交直播在实时通信基础设施需求上的差异。",
};

export default async function AIVoiceInfrastructurePage() {
  const articleRoot = path.join(process.cwd(), "articles");
  const zhPath = path.join(articleRoot, "AI语音对基础设施需求的特性.md");
  const enPath = path.join(articleRoot, "Infrastructure Requirements for AI Voice.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      enMarkdown={enMarkdown}
      enTitle="How AI Voice Changes Infrastructure Requirements"
      zhMarkdown={zhMarkdown}
      zhTitle="AI语音对基础设施需求的特性"
    />
  );
}
