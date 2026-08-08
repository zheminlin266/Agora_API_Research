import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("openai-livekit-relationship");

export default function OpenAILiveKitRelationshipPage() {
  return <ManifestArticlePage id="openai-livekit-relationship" />;
}
