"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

import type { SearchResult } from "@/lib/site-search";
import { useSitePreferences } from "@/components/site-preferences";

import styles from "./site-search.module.css";

const MAX_QUERY_LENGTH = 80;

type SearchErrorCode = "too_long" | "unavailable" | "invalid_response";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isSearchResult(value: unknown): value is SearchResult {
  if (!isRecord(value)) return false;
  return (
    typeof value.articleTitle === "string" &&
    typeof value.href === "string" &&
    typeof value.sectionTitle === "string" &&
    typeof value.snippet === "string"
  );
}

function parseSearchResults(value: unknown): SearchResult[] {
  if (!isRecord(value) || !Array.isArray(value.results) || !value.results.every(isSearchResult)) {
    throw new Error("Invalid search response");
  }
  return value.results;
}

function errorCodeFromResponse(value: unknown): SearchErrorCode {
  if (isRecord(value) && value.code === "QUERY_TOO_LONG") return "too_long";
  return "unavailable";
}

function errorMessage(language: "zh" | "en", code: SearchErrorCode) {
  if (code === "too_long") {
    return language === "zh" ? "搜索关键词不能超过 80 个字符" : "Search queries must be 80 characters or fewer";
  }
  return language === "zh" ? "搜索暂时不可用，请稍后重试" : "Search is temporarily unavailable. Please try again later";
}

export function SiteSearch() {
  const [open, setOpen] = useState(false);
  const [closing, setClosing] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<SearchErrorCode | null>(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const restoreFocusRef = useRef<HTMLElement | null>(null);
  const { language } = useSitePreferences();

  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const openSearch = useCallback(() => {
    if (closeTimer.current) {
      clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }
    const activeElement = document.activeElement;
    restoreFocusRef.current = activeElement instanceof HTMLElement && activeElement !== document.body
      ? activeElement
      : triggerRef.current;
    setClosing(false);
    setOpen(true);
  }, []);

  const close = useCallback(() => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    setClosing(true);
    closeTimer.current = setTimeout(() => {
      setOpen(false);
      setClosing(false);
      setQuery("");
      setResults([]);
      setError(null);
      setSelectedIndex(0);
      closeTimer.current = null;
      restoreFocusRef.current?.focus();
      restoreFocusRef.current = null;
    }, 180);
  }, []);

  useEffect(() => () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    restoreFocusRef.current = null;
  }, []);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        if (open) close();
        else openSearch();
        return;
      }
      if (event.key === "Escape" && open) {
        event.preventDefault();
        close();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, close, openSearch]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    const controller = new AbortController();
    fetch(
      `/api/search/?q=${encodeURIComponent(query)}&lang=${language}`,
      { signal: controller.signal },
    )
      .then(async (res) => {
        if (cancelled) return;
        const data: unknown = await res.json().catch(() => null);
        if (!res.ok) {
          throw { code: errorCodeFromResponse(data) };
        }
        setResults(parseSearchResults(data));
        setSelectedIndex(0);
      })
      .catch((reason: unknown) => {
        if (cancelled || (reason instanceof DOMException && reason.name === "AbortError")) return;
        setResults([]);
        setSelectedIndex(0);
        setError(
          isRecord(reason) && (reason.code === "too_long" || reason.code === "unavailable")
            ? reason.code
            : "invalid_response",
        );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [query, language]);

  useEffect(() => {
    setSelectedIndex((previous) => results.length === 0 ? 0 : Math.min(previous, results.length - 1));
  }, [results.length]);

  useEffect(() => {
    if (!open) return;
    inputRef.current?.focus();
  }, [open]);

  useEffect(() => {
    const item = listRef.current?.children[selectedIndex] as HTMLElement | undefined;
    item?.scrollIntoView({ block: "nearest" });
  }, [selectedIndex]);

  function handleInputKeyDown(event: React.KeyboardEvent) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setSelectedIndex((prev) => results.length === 0 ? 0 : Math.min(prev + 1, results.length - 1));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, 0));
    } else if (event.key === "Enter" && results[selectedIndex]) {
      event.preventDefault();
      window.location.href = results[selectedIndex].href;
      close();
    } else if (event.key === "Escape") {
      close();
    }
  }

  return (
    <>
      <button
        ref={triggerRef}
        className="control-button icon-button"
        onClick={openSearch}
        aria-label={language === "zh" ? "搜索文章" : "Search articles"}
        title={language === "zh" ? "搜索文章" : "Search articles"}
      >
        <span className="control-icon">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
        </span>
      </button>

      {open && typeof document !== "undefined" && createPortal(
        <div
          className={closing ? styles.overlay + " " + styles.closing : styles.overlay}
          onClick={close}
        >
          <dialog
            className={closing ? styles.dialog + " " + styles.closing : styles.dialog}
            open
            onClick={(event) => event.stopPropagation()}
            aria-label={language === "zh" ? "搜索文章" : "Search articles"}
          >
            <div className={styles.inputWrapper}>
              <svg
                className={styles.searchIcon}
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
              <input
                ref={inputRef}
                className={styles.input}
                type="text"
                maxLength={MAX_QUERY_LENGTH}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={handleInputKeyDown}
                placeholder={language === "zh" ? "搜索文章标题或内容…" : "Search articles…"}
                aria-label={language === "zh" ? "搜索关键词" : "Search keyword"}
              />
              {query && (
                <button
                  className={styles.clearButton}
                  onClick={() => { setQuery(""); setResults([]); setError(null); }}
                  aria-label={language === "zh" ? "清除搜索" : "Clear search"}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <path d="M18 6 6 18M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>

            {loading && <div className={styles.status}>{language === "zh" ? "搜索中…" : "Searching…"}</div>}

            {!loading && results.length > 0 && (
              <ul ref={listRef} className={styles.results} role="listbox">
                {results.map((result, index) => (
                  <li key={`${result.href}-${index}`} role="option" aria-selected={index === selectedIndex}>
                    <a
                      className={`${styles.resultItem} ${index === selectedIndex ? styles.selected : ""}`}
                      href={result.href}
                      onClick={close}
                      onMouseEnter={() => setSelectedIndex(index)}
                    >
                      <span className={styles.resultTitle}>{result.sectionTitle}</span>
                      <span className={styles.resultArticle}>{result.articleTitle}</span>
                      {result.snippet && (
                        <span className={styles.snippet}>{result.snippet}</span>
                      )}
                    </a>
                  </li>
                ))}
              </ul>
            )}

            {!loading && error && (
              <div className={styles.status} role="status" aria-live="polite">
                {errorMessage(language, error)}
              </div>
            )}

            {!loading && !error && query.trim() && results.length === 0 && (
              <div className={styles.status}>
                {language === "zh" ? "未找到相关结果" : "No results found"}
              </div>
            )}
          </dialog>
        </div>,
        document.body,
      )}
    </>
  );
}
