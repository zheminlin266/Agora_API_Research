import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("ai-rtc-moats");

export default function AIRTCMoatsPage() {
  return <ManifestArticlePage id="ai-rtc-moats" />;
}
