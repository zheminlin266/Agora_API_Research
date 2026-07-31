import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

export const metadata: Metadata = {
  title: "声网员工人数变化 | Agora Equity Research",
  description: "Agora 2020—2025 年员工人数、岗位结构及组织收缩分析。",
};

export default async function AgoraEmployeeHeadcountChangesPage() {
  const zhPath = path.join(process.cwd(), "articles", "员工人数变化.md");
  const enPath = path.join(process.cwd(), "articles", "employee_headcount_changes.md");
  const [zhMarkdown, enMarkdown] = await Promise.all([
    readFile(zhPath, "utf8"),
    readFile(enPath, "utf8"),
  ]);

  return (
    <LocalizedMarkdownArticle
      enMarkdown={enMarkdown}
      enTitle="Agora Employee Headcount Changes"
      zhMarkdown={zhMarkdown}
      zhTitle="声网员工人数变化"
    />
  );
}
