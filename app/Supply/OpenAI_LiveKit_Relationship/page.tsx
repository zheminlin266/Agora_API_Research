import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";
import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "OpenAI 与 LiveKit 关系 | Agora Equity Research",
  description: "复盘 OpenAI AI 语音发展与 LiveKit 演进，以及双方合作关系的变化。",
};

export default async function OpenAILiveKitRelationshipPage() {
  const zhPath = path.join(process.cwd(), "articles", "OpenAI与LiveKit关系.md");
  const enPath = path.join(process.cwd(), "articles", "OpenAI and LiveKit Relationship.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      enMarkdown={enMarkdown}
      enTitle="OpenAI and LiveKit: From Co-Developing ChatGPT Voice to a Voice-Agent Infrastructure Ecosystem"
      zhMarkdown={zhMarkdown}
      zhTitle="OpenAI 与 LiveKit：从 ChatGPT 语音模式共研，到语音代理基础设施生态"
    />
  );
}
