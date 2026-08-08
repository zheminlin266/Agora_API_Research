import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("employee-headcount-changes");

export default function AgoraEmployeeHeadcountChangesPage() {
  return <ManifestArticlePage id="employee-headcount-changes" />;
}
