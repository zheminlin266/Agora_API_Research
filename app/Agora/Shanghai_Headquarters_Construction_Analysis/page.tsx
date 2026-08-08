import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("shanghai-headquarters-construction");

export default function ShanghaiHeadquartersConstructionAnalysisPage() {
  return <ManifestArticlePage id="shanghai-headquarters-construction" />;
}
