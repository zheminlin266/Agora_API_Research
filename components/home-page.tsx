"use client";

import { LocalizedMarkdownArticle } from "@/components/localized-markdown-article";

type HomePageContentProps = {
  zhMarkdown: string;
  enMarkdown: string;
};

export function HomePageContent({ zhMarkdown, enMarkdown }: HomePageContentProps) {
  return (
    <LocalizedMarkdownArticle
      articleClassName="home-article"
      enMarkdown={enMarkdown}
      enTitle="Agora — Key Takeaways"
      imageBasePath="/articles/agora-key-takeaways"
      showHeader={false}
      zhMarkdown={zhMarkdown}
      zhTitle="声网-主要观点"
    />
  );
}