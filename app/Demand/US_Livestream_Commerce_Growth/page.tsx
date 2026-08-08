import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("us-livestream-commerce-growth");

export default function USLivestreamCommerceGrowthPage() {
  return <ManifestArticlePage id="us-livestream-commerce-growth" />;
}
