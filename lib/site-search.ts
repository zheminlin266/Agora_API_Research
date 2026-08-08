import { readFile } from "node:fs/promises";
import path from "node:path";

export type SearchLanguage = "zh" | "en";
export type SearchResult = {
  articleTitle: string;
  href: string;
  sectionTitle: string;
  snippet: string;
};

type SearchSection = Omit<SearchResult, "snippet"> & {
  language: SearchLanguage;
  text: string;
};

type ArticleDefinition = {
  href: string;
  zh: { file: string; title: string };
  en: { file: string; title: string };
};

const articles: ArticleDefinition[] = [
  {
    href: "/Demand/RTC_industry_demand/",
    zh: { file: "RTC行业需求.md", title: "RTC行业需求" },
    en: { file: "RTC Industry Demand.md", title: "RTC Industry Demand" },
  },
  {
    href: "/Demand/US_Livestream_Commerce_Growth/",
    zh: { file: "美国直播电商增长情况.md", title: "美国直播电商增长情况" },
    en: { file: "U.S. Livestream Commerce Growth.md", title: "U.S. Livestream Commerce Growth" },
  },
  {
    href: "/Demand/AI_Voice_Infrastructure/",
    zh: { file: "AI语音对基础设施需求的特性.md", title: "AI语音对基础设施需求的特性" },
    en: { file: "Infrastructure Requirements for AI Voice.md", title: "How AI Voice Changes Infrastructure Requirements" },
  },
  {
    href: "/Supply/RTC_supply/",
    zh: { file: "RTC行业供给.md", title: "RTC 行业供给" },
    en: { file: "RTC_industry_supply.en.md", title: "RTC Industry Supply" },
  },
  {
    href: "/Supply/AI_RTC_moats/",
    zh: { file: "AI对RTC业务护城河的影响.md", title: "AI对RTC业务护城河的影响" },
    en: { file: "Impact_of_AI_on_RTC_Business_Moats.md", title: "Impact of AI on RTC Business Moats" },
  },
  {
    href: "/Supply/OpenAI_LiveKit_Relationship/",
    zh: { file: "OpenAI与LiveKit关系.md", title: "OpenAI 与 LiveKit：从 ChatGPT 语音模式共研，到语音代理基础设施生态" },
    en: { file: "OpenAI and LiveKit Relationship.md", title: "OpenAI and LiveKit: From Co-Developing ChatGPT Voice to a Voice-Agent Infrastructure Ecosystem" },
  },
  {
    href: "/Agora/Customer_Scenarios_Competitive_Analysis/",
    zh: { file: "声网客户场景和竞争分析.md", title: "声网生存空间和迁移案例" },
    en: { file: "agora_customer_scenarios_and_competitive_analysis.md", title: "Agora's Competitive Space and Migration Cases" },
  },
  {
    href: "/Agora/Whatnot_Agora_Partnership/",
    zh: { file: "Whatnot & Agora直播合作.md", title: "Whatnot & Agora直播合作案例" },
    en: { file: "Whatnot & Agora Livestream Partnership.md", title: "Whatnot & Agora Livestream Partnership" },
  },
  {
    href: "/Agora/Equity_Ownership_Share_Repurchase_Analysis/",
    zh: { file: "股权结构与回购分析.md", title: "股权结构与回购分析" },
    en: { file: "Equity Ownership and Share Repurchase Analysis.md", title: "Equity Ownership and Share Repurchase Analysis" },
  },
  {
    href: "/Agora/Employee_Headcount_Changes/",
    zh: { file: "员工人数变化.md", title: "声网员工人数变化" },
    en: { file: "employee_headcount_changes.md", title: "Agora Employee Headcount Changes" },
  },
  {
    href: "/Agora/Shanghai_Headquarters_Construction_Analysis/",
    zh: { file: "上海总部建设分析.md", title: "上海总部建设分析" },
    en: { file: "Shanghai_Headquarters_Construction_Analysis_EN.md", title: "Shanghai Headquarters Construction Analysis" },
  },
];

function headingId(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^\w\u4e00-\u9fff\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function plainText(markdown: string) {
  return markdown
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/\\([*_#[\]`])/g, "$1")
    .replace(/[*_`>#|]/g, " ")
    .replace(/^ {0,3}(?:[-+]\s+|\d+[.)]\s+)/gm, "")
    .replace(/\s+/g, " ")
    .trim();
}

function sectionsFromMarkdown(
  markdown: string,
  language: SearchLanguage,
  articleTitle: string,
  articleHref: string,
) {
  const sections: SearchSection[] = [];
  const lines = markdown.replace(/\r/g, "").split("\n");
  let sectionTitle = articleTitle;
  let sectionHref = `${articleHref}#top`;
  let content: string[] = [];

  function flush() {
    const text = plainText(content.join("\n"));
    if (text || sectionTitle) {
      sections.push({ articleTitle, href: sectionHref, language, sectionTitle, text });
    }
    content = [];
  }

  for (const line of lines) {
    const normalizedLine = line.replace(/^(\s*)\\(#{1,6}\s+)/, "$1$2");
    const heading = normalizedLine.match(/^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);
    if (!heading) {
      content.push(line);
      continue;
    }

    const title = plainText(heading[2]);
    if (heading[1].length === 1 && sections.length === 0 && content.every((value) => !value.trim())) {
      continue;
    }

    flush();
    sectionTitle = title;
    sectionHref = `${articleHref}#${headingId(title) || "top"}`;
  }

  flush();
  return sections;
}

let sectionCache: Promise<SearchSection[]> | undefined;

async function loadSections() {
  const articleRoot = path.join(process.cwd(), "articles");
  const groups = await Promise.allSettled(articles.flatMap((article) => (
    (["zh", "en"] as const).map(async (language) => {
      const definition = article[language];
      const markdown = await readFile(path.join(articleRoot, definition.file), "utf8");
      return sectionsFromMarkdown(markdown, language, definition.title, article.href);
    })
  )));
  const rejected = groups.filter((result): result is PromiseRejectedResult => result.status === "rejected");
  const sections = groups
    .filter((result): result is PromiseFulfilledResult<SearchSection[]> => result.status === "fulfilled")
    .flatMap((result) => result.value);

  if (rejected.length > 0) {
    console.error(`Search index skipped ${rejected.length} article file(s).`, rejected.map((result) => result.reason));
  }
  if (sections.length === 0) {
    throw new Error("Search index contains no readable article files.");
  }
  return sections;
}

function makeSnippet(text: string, query: string) {
  if (!text) return "";
  const index = text.toLocaleLowerCase().indexOf(query);
  const radius = 95;
  const start = index < 0 ? 0 : Math.max(0, index - radius);
  const end = index < 0
    ? Math.min(text.length, radius * 2)
    : Math.min(text.length, index + query.length + radius);
  return `${start > 0 ? "…" : ""}${text.slice(start, end).trim()}${end < text.length ? "…" : ""}`;
}

export async function searchArticles(rawQuery: string, language: SearchLanguage, limit = 10) {
  const query = rawQuery.trim().toLocaleLowerCase();
  if (!query) return [];
  if (!sectionCache) {
    const pending = loadSections();
    sectionCache = pending.catch((error) => {
      sectionCache = undefined;
      throw error;
    });
  }

  const matches = (await sectionCache)
    .filter((section) => section.language === language)
    .map((section) => {
      const article = section.articleTitle.toLocaleLowerCase();
      const title = section.sectionTitle.toLocaleLowerCase();
      const text = section.text.toLocaleLowerCase();
      const articleMatch = section.href.endsWith("#top") && article.includes(query);
      if (!articleMatch && !title.includes(query) && !text.includes(query)) return null;

      let score = articleMatch ? (article === query ? 120 : 45) : 0;
      score += title === query ? 100 : title.startsWith(query) ? 75 : title.includes(query) ? 60 : 0;
      const textIndex = text.indexOf(query);
      if (textIndex >= 0) score += Math.max(5, 25 - Math.floor(textIndex / 120));

      return {
        score,
        result: {
          articleTitle: section.articleTitle,
          href: section.href,
          sectionTitle: section.sectionTitle,
          snippet: makeSnippet(section.text, query),
        } satisfies SearchResult,
      };
    })
    .filter((match): match is NonNullable<typeof match> => match !== null)
    .sort((a, b) => b.score - a.score);

  return matches.slice(0, limit).map((match) => match.result);
}
