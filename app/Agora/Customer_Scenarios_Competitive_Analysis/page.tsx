import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("customer-scenarios-competitive-analysis");

export default function AgoraCustomerScenariosPage() {
  return <ManifestArticlePage id="customer-scenarios-competitive-analysis" />;
}
