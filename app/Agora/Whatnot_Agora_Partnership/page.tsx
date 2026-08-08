import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("whatnot-agora-partnership");

export default function WhatnotAgoraPartnershipPage() {
  return <ManifestArticlePage id="whatnot-agora-partnership" />;
}
