"use client";

import styles from "./agora-key-metrics.module.css";

import { useEffect } from "react";

import metricsData from "@/data/agora_quarterly_key_metrics.json";
import { SiteHeader } from "@/components/site-header";
import { useSitePreferences } from "@/components/site-preferences";

type MetricValue = string | number | null;

export function AgoraKeyMetricsPageContent() {
  const { language } = useSitePreferences();
  const isEnglish = language === "en";
  const title = isEnglish ? "Agora Key Metrics" : "声网核心数据";
  const headers = isEnglish ? metricsData.headers.en : metricsData.headers.zh;

  useEffect(() => {
    document.title = `${title} | Agora Equity Research`;
  }, [title]);

  return (
    <>
      <SiteHeader />
      <main className={`site-main metrics-page ${styles.metricsScope}`} id="top">
        <header className="metrics-header rise delay-1">
          <h1>{title}</h1>
        </header>

        <section
          aria-label={title}
          className="metrics-table-frame rise delay-2"
          role="region"
          tabIndex={0}
        >
          <table className="metrics-table">
            <thead>
              <tr>
                {headers.map((header) => <th key={header} scope="col">{header}</th>)}
              </tr>
            </thead>
            <tbody>
              {metricsData.rows.map((row, rowIndex) => (
                <tr key={String(row[0] ?? rowIndex)}>
                  {row.map((value: MetricValue, cellIndex) => (
                    <td key={`${rowIndex}-${cellIndex}`} className={cellIndex === 0 ? "metrics-table__quarter" : undefined}>
                      {value === null ? "" : value}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </>
  );
}
