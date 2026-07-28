"use client";

import { useEffect } from "react";

import { MarkdownArticle } from "@/components/markdown-article";
import { useSitePreferences } from "@/components/site-preferences";

type LocalizedMarkdownArticleProps = {
  zhMarkdown: string;
  enMarkdown: string;
  zhTitle?: string;
  enTitle?: string;
};

export function LocalizedMarkdownArticle({
  zhMarkdown,
  enMarkdown,
  zhTitle,
  enTitle,
}: LocalizedMarkdownArticleProps) {
  const { language } = useSitePreferences();
  const isEnglish = language === "en";
  const articleTitle = isEnglish
    ? enTitle ?? "RTC Industry Supply"
    : zhTitle ?? "RTC 行业供给";

  useEffect(() => {
    const timer = window.setTimeout(() => {
      document.title = articleTitle + " | Agora Equity Research";
    }, 100);

    return () => window.clearTimeout(timer);
  }, [isEnglish]);

  return (
    <MarkdownArticle
      backToTopLabel={isEnglish ? "Back to top" : "返回顶部"}
      articleTitle={articleTitle}
      markdown={isEnglish ? enMarkdown : zhMarkdown}
      publicationDateLabel={isEnglish ? "July 2026" : "2026年7月"}
      tocLabels={isEnglish ? {
        ariaLabel: "Table of contents",
        collapse: "Collapse table of contents",
        expand: "Expand table of contents",
        title: "Contents",
      } : {
        ariaLabel: "目录",
        collapse: "收起文章目录",
        expand: "展开文章目录",
        title: "目录",
      }}
    />
  );
}
