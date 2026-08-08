import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("rtc-industry-demand");

export default function RTCIndustryDemandPage() {
  return <ManifestArticlePage id="rtc-industry-demand" />;
}
