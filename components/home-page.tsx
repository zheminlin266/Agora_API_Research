"use client";

import { SiteHeader } from "@/components/site-header";

export function HomePageContent() {
  return (
    <>
      <SiteHeader />
      <main className="site-main construction-page" id="top">
        <p className="construction-label">建设中</p>
      </main>
    </>
  );
}