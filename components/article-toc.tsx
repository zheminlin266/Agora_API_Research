"use client";

import { useEffect, useState } from "react";

export type ArticleTocItem = {
  id: string;
  label: string;
  level: number;
};

export type ArticleTocLabels = {
  ariaLabel: string;
  collapse: string;
  expand: string;
  title: string;
};

const defaultLabels: ArticleTocLabels = {
  ariaLabel: "目录",
  collapse: "收起文章目录",
  expand: "展开文章目录",
  title: "目录",
};

export function ArticleToc({ items, labels = defaultLabels }: { items: ArticleTocItem[]; labels?: ArticleTocLabels }) {
  const [collapsed, setCollapsed] = useState(false);
  const [activeId, setActiveId] = useState(items[0]?.id ?? "");
  const minimumHeadingLevel = items.reduce(
    (minimum, item) => Math.min(minimum, item.level),
    items[0]?.level ?? 0,
  );

  useEffect(() => {
    const headings = items
      .map((item) => document.getElementById(item.id))
      .filter((heading): heading is HTMLElement => Boolean(heading));
    if (!headings.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((left, right) => left.boundingClientRect.top - right.boundingClientRect.top);
        if (visible[0]?.target.id) setActiveId(visible[0].target.id);
      },
      { rootMargin: "-96px 0px -62% 0px", threshold: [0, 1] },
    );

    headings.forEach((heading) => observer.observe(heading));
    return () => observer.disconnect();
  }, [items]);

  return (
    <aside className={`article-toc${collapsed ? " article-toc--collapsed" : ""}`} aria-label={labels.ariaLabel}>
      <button
        aria-controls="article-toc-list"
        aria-expanded={!collapsed}
        aria-label={collapsed ? labels.expand : labels.collapse}
        className="article-toc__toggle"
        onClick={() => setCollapsed((value) => !value)}
        type="button"
      >
        <span aria-hidden="true" className="article-toc__icon">
          <span />
          <span />
          <span />
        </span>
        <span className="article-toc__label">{labels.title}</span>
      </button>
      <nav
        aria-hidden={collapsed}
        aria-label={labels.ariaLabel}
        className="article-toc__nav"
        id="article-toc-list"
        tabIndex={collapsed ? -1 : 0}
      >
        {items.map((item) => (
          <a
            className={[
              "article-toc__link",
              "article-toc__link--level-" + item.level,
              "article-toc__link--depth-" + Math.max(0, item.level - minimumHeadingLevel),
              activeId === item.id ? "is-active" : "",
            ].filter(Boolean).join(" ")}
            href={"#" + item.id}
            key={item.id}
            tabIndex={collapsed ? -1 : 0}
          >
            {item.label}
          </a>
        ))}
      </nav>
    </aside>
  );
}
