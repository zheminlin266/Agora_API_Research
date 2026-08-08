import type { Metadata } from "next";

import { ManifestArticlePage } from "@/components/manifest-article-page";
import { getArticleMetadata } from "@/lib/content-manifest";

export const metadata: Metadata = getArticleMetadata("ai-voice-infrastructure");

export default function AIVoiceInfrastructurePage() {
  return <ManifestArticlePage id="ai-voice-infrastructure" />;
}
