import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("rtc-supply");

export default function SupplyArticlePage() {
  return <ManifestArticlePage id="rtc-supply" />;
}
