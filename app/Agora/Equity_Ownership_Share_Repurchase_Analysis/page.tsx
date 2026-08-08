import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("equity-ownership-share-repurchase");

export default function AgoraEquityOwnershipPage() {
  return <ManifestArticlePage id="equity-ownership-share-repurchase" />;
}
