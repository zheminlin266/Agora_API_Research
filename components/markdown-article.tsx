import type { ReactNode } from "react";

import { BackToTop } from "@/components/back-to-top";
import { SiteHeader } from "@/components/site-header";
import { ArticleToc, type ArticleTocItem, type ArticleTocLabels } from "@/components/article-toc";

type TableBlock = {
  kind: "table";
  headers: string[];
  rows: string[][];
};

type ArticleBlock =
  | { kind: "heading"; level: number; content: string }
  | { kind: "paragraph"; content: string }
  | { kind: "image"; alt: string; src: string }
  | { kind: "code"; content: string }
  | { kind: "ordered-list" | "unordered-list"; items: string[] }
  | TableBlock;

function normalizeMarkdownSyntax(line: string) {
  return line
    .replace(/^(\s*)\\(#{1,6}\s+)/, "$1$2")
    .replace(/^(\s*)\\([-*+]\s+)/, "$1$2")
    .replace(/^(\s*)(\d+)\\([.)]\s+)/, "$1$2$3")
    .replace(/^(\s*)\\(\d+[.)]\s+)/, "$1$2");
}

function isHeading(line: string) {
  return /^ {0,3}#{1,6}\s+/.test(normalizeMarkdownSyntax(line));
}

function isListItem(line: string) {
  return /^ {0,3}(?:[-*+]\s+|\d+[.)]\s+)/.test(normalizeMarkdownSyntax(line));
}

function isTableSeparator(line: string) {
  return /^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?\s*$/.test(line);
}

function parseTableRow(line: string) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function normalizeInlineMarkdown(value: string) {
  return value.replace(/\\([*_])/g, "$1");
}

function isBlockStart(line: string) {
  return isHeading(line) || isListItem(line) || line.trim().startsWith("|") || line.trim().startsWith("```");
}

function parseBlocks(markdown: string): ArticleBlock[] {
  const lines = markdown.replace(/\r/g, "").split("\n");
  const blocks: ArticleBlock[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index].trimEnd();
    if (!line.trim()) {
      index += 1;
      continue;
    }

    const heading = normalizeMarkdownSyntax(line).match(/^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);
    if (heading) {
      blocks.push({ kind: "heading", level: heading[1].length, content: heading[2] });
      index += 1;
      continue;
    }

    if (line.trim().startsWith("```")) {
      const codeLines: string[] = [];
      index += 1;
      while (index < lines.length && !lines[index].trim().startsWith("```")) {
        codeLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) index += 1;
      blocks.push({ kind: "code", content: codeLines.join("\n") });
      continue;
    }
    const image = line.match(/^!\[([^\]]*)\]\(([^)\s]+)\)\s*$/);
    if (image) {
      blocks.push({ kind: "image", alt: image[1], src: image[2] });
      index += 1;
      continue;
    }

    let tableSeparatorIndex = -1;
    if (line.trim().startsWith("|")) {
      tableSeparatorIndex = index + 1;
      while (tableSeparatorIndex < lines.length && !lines[tableSeparatorIndex].trim()) tableSeparatorIndex += 1;
    }
    if (tableSeparatorIndex >= 0 && isTableSeparator(lines[tableSeparatorIndex] ?? "")) {
      const headers = parseTableRow(line);
      index = tableSeparatorIndex + 1;
      const rows: string[][] = [];
      while (index < lines.length) {
        if (!lines[index].trim()) {
          let nextIndex = index + 1;
          while (nextIndex < lines.length && !lines[nextIndex].trim()) nextIndex += 1;
          if (nextIndex < lines.length && lines[nextIndex].trim().startsWith("|")) {
            index = nextIndex;
            continue;
          }
          break;
        }
        if (!lines[index].trim().startsWith("|")) break;
        rows.push(parseTableRow(lines[index]));
        index += 1;
      }
      blocks.push({ kind: "table", headers, rows });
      continue;
    }

    const ordered = normalizeMarkdownSyntax(line).match(/^ {0,3}\d+[.)]\s+(.+)/);
    if (ordered) {
      const items: string[] = [];
      while (index < lines.length) {
        if (!lines[index].trim()) {
          let nextIndex = index + 1;
          while (nextIndex < lines.length && !lines[nextIndex].trim()) nextIndex += 1;
          const nextItem = normalizeMarkdownSyntax(lines[nextIndex] ?? "").match(/^ {0,3}\d+[.)]\s+(.+)/);
          if (nextItem) {
            index = nextIndex;
            continue;
          }
          break;
        }
        const item = normalizeMarkdownSyntax(lines[index]).match(/^ {0,3}\d+[.)]\s+(.+)/);
        if (!item) break;
        items.push(item[1]);
        index += 1;
      }
      blocks.push({ kind: "ordered-list", items });
      continue;
    }

    const unordered = normalizeMarkdownSyntax(line).match(/^ {0,3}[-*+]\s+(.+)/);
    if (unordered) {
      const items: string[] = [];
      while (index < lines.length) {
        const item = normalizeMarkdownSyntax(lines[index]).match(/^ {0,3}[-*+]\s+(.+)/);
        if (!item) break;
        items.push(item[1]);
        index += 1;
      }
      blocks.push({ kind: "unordered-list", items });
      continue;
    }

    const paragraph: string[] = [line.trim()];
    index += 1;
    while (index < lines.length && lines[index].trim() && !isBlockStart(lines[index])) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    blocks.push({ kind: "paragraph", content: paragraph.join(" ") });
  }

  return blocks;
}

function normalizeArticleHref(href: string) {
  try {
    const url = new URL(href);
    if (url.hostname === "agora.zhemin.ltd" || url.hostname === "www.agora.zhemin.ltd") {
      return `${url.pathname}${url.search}${url.hash}`;
    }
  } catch {
    // Keep malformed or non-URL values unchanged for the renderer to handle.
  }
  return href;
}

function renderInline(value: string, keyPrefix: string): ReactNode[] {
  const normalizedValue = normalizeInlineMarkdown(value);
  const nodes: ReactNode[] = [];
  const pattern = /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)|\*\*([^*]+)\*\*|__([^_]+)__|`([^`]+)`|\*([^*]+)\*/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;

  while ((match = pattern.exec(normalizedValue))) {
    if (match.index > lastIndex) nodes.push(normalizedValue.slice(lastIndex, match.index));
    if (match[1] && match[2]) {
      nodes.push(
        <a className="article-link" href={normalizeArticleHref(match[2])} key={`${keyPrefix}-${key}`} rel="noreferrer" target="_blank">
          {match[1]}
        </a>,
      );
    } else if (match[3] || match[4]) {
      nodes.push(
        <strong key={`${keyPrefix}-${key}`}>
          {renderInline(match[3] ?? match[4] ?? "", `${keyPrefix}-${key}-strong`)}
        </strong>,
      );
    } else if (match[5]) {
      nodes.push(<code key={`${keyPrefix}-${key}`}>{match[5]}</code>);
    } else {
      nodes.push(<em key={`${keyPrefix}-${key}`}>{match[6]}</em>);
    }
    key += 1;
    lastIndex = pattern.lastIndex;
  }

  if (lastIndex < normalizedValue.length) nodes.push(normalizedValue.slice(lastIndex));
  return nodes;
}

function renderList(items: string[], ordered: boolean) {
  const List = ordered ? "ol" : "ul";
  return (
    <List>
      {items.map((item, index) => <li key={`${ordered ? "ol" : "ul"}-${index}`}>{renderInline(item, `list-${index}`)}</li>)}
    </List>
  );
}

function getHeadingId(value: string, index: number) {
  const slug = value
    .toLowerCase()
    .trim()
    .replace(/[^\w\u4e00-\u9fff\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "section-" + index;
}

function getTableClass(headers: string[]) {
  const firstHeader = headers[0]?.trim().toLowerCase() ?? "";
  if (firstHeader === "供应商" || firstHeader === "provider") return "article-table article-table--entry";
  if (firstHeader.includes("原供应商") || firstHeader.startsWith("original provider")) return "article-table article-table--exit";
  if (firstHeader === "下游场景" || firstHeader === "downstream use case") return "article-table article-table--participant-mix";
  if (firstHeader === "年份" || firstHeader === "year") return "article-table article-table--history";
  if (firstHeader === "rtc供应层次" || firstHeader === "rtc supply layer") return "article-table article-table--supply";
  if (firstHeader === "阶段" || firstHeader === "stage") return "article-table article-table--wide article-table--relationship";
  if (headers.length >= 5) return "article-table article-table--wide";
  return "article-table article-table--comparison";
}
type MarkdownArticleProps = {
  markdown: string;
  language?: "zh" | "en";
  articleTitle?: string;
  articleClassName?: string;
  imageBasePath?: string;
  showHeader?: boolean;
  showToc?: boolean;
  publicationDateLabel?: string;
  backToTopLabel?: string;
  tocLabels?: ArticleTocLabels;
};

export function MarkdownArticle({
  markdown,
  language = "zh",
  articleTitle,
  articleClassName,
  imageBasePath,
  showHeader = true,
  showToc = true,
  publicationDateLabel = "2026年7月",
  backToTopLabel = "返回顶部",
  tocLabels,
}: MarkdownArticleProps) {
  const blocks = parseBlocks(markdown);
  const titleBlockIndex = articleTitle
    ? blocks.findIndex((block) => block.kind === "heading" && block.level === 1)
    : blocks.findIndex((block) => block.kind === "heading");
  const titleBlock = titleBlockIndex >= 0 ? blocks[titleBlockIndex] : undefined;
  const title = articleTitle ?? (titleBlock?.kind === "heading" ? titleBlock.content : undefined);
  const contentBlocks = titleBlockIndex >= 0 ? blocks.slice(titleBlockIndex + 1) : blocks;
  const tocItems: ArticleTocItem[] = contentBlocks.flatMap((block, index) => block.kind === "heading" ? [{ id: getHeadingId(block.content, index), label: block.content, level: block.level }] : []);
  const resolveImageSrc = (src: string) => {
    if (!imageBasePath || /^(?:[a-z]+:)?\//i.test(src)) return src;
    return `${imageBasePath.replace(/\/$/, "")}/${src}`;
  };

  return (
    <>
      <SiteHeader />
      {showToc && <ArticleToc items={tocItems} labels={tocLabels} />}
      <main className={["site-main", "article-page", articleClassName].filter(Boolean).join(" ")} id="top">
        {showHeader && (
          <header className="article-header rise delay-1">
            <h1>{title ? renderInline(title, "article-title") : "RTC industry supply"}</h1>
            <div className="article-meta"><time dateTime="2026-07">{publicationDateLabel}</time></div>
          </header>
        )}

        <article className="article-content rise delay-2">
          {contentBlocks.map((block, index) => {
            if (block.kind === "heading") {
              const Heading = `h${Math.min(block.level, 4)}` as "h2" | "h3" | "h4";
              return <Heading id={getHeadingId(block.content, index)} key={`heading-${index}`}>{renderInline(block.content, `heading-${index}`)}</Heading>;
            }
            if (block.kind === "paragraph") {
              if (block.content.includes("agora-share-repurchase-quarterly.html")) {
                const chartLanguage = language === "en" ? "en" : "zh";
                return (
                  <div className="article-chart-embed" key={`chart-${index}`}>
                    <iframe
                      height="560"
                      loading="lazy"
                      src={`/agora-share-repurchase-quarterly.html?embed=1&lang=${chartLanguage}`}
                      title={chartLanguage === "en" ? "Interactive quarterly share repurchase chart" : "季度回购交互图表"}
                    />
                  </div>
                );
              }
              return <p key={`paragraph-${index}`}>{renderInline(block.content, `paragraph-${index}`)}</p>;
            }
            if (block.kind === "code") return <pre key={`code-${index}`}><code>{block.content}</code></pre>;
            if (block.kind === "image") {
              return (
                <figure className="article-image" key={`image-${index}`}>
                  <img alt={block.alt} loading="lazy" src={resolveImageSrc(block.src)} />
                </figure>
              );
            }
            if (block.kind === "ordered-list") return <div key={`ordered-${index}`}>{renderList(block.items, true)}</div>;
            if (block.kind === "unordered-list") return <div key={`unordered-${index}`}>{renderList(block.items, false)}</div>;

            if (block.kind !== "table") return null;

            return (
              <div className="article-table-wrap" key={`table-${index}`}>
                <table className={getTableClass(block.headers)}>
                  <thead>
                    <tr>{block.headers.map((header, cellIndex) => <th key={`header-${cellIndex}`}>{renderInline(header, `header-${cellIndex}`)}</th>)}</tr>
                  </thead>
                  <tbody>
                    {block.rows.map((row, rowIndex) => (
                      <tr key={`row-${rowIndex}`}>
                        {block.headers.map((_, cellIndex) => <td key={`cell-${rowIndex}-${cellIndex}`}>{renderInline(row[cellIndex] ?? "", `cell-${rowIndex}-${cellIndex}`)}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          })}
        </article>

        <footer className="article-footer rise delay-3">
          <BackToTop label={backToTopLabel} />
          <a href="https://www.zhemin.ltd">@Zhemin</a>
        </footer>
      </main>
    </>
  );
}
