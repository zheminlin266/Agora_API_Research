import type { Metadata } from "next";
import Script from "next/script";

import { SitePreferencesProvider } from "@/components/site-preferences";

import "./globals.css";

export const metadata: Metadata = {
  title: "Agora Research",
  description: "聚焦实时互动行业需求、供给格局与声网竞争优势的独立研究。",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body>
        <Script id="theme-init" strategy="beforeInteractive">{`
          try {
            const saved = localStorage.getItem("agora-research-theme");
            const system = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
            document.documentElement.dataset.theme = saved === "dark" || saved === "light" ? saved : system;
          } catch {}
        `}</Script>
        <SitePreferencesProvider>{children}</SitePreferencesProvider>
      </body>
    </html>
  );
}
