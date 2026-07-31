import type { Metadata } from "next";

import { AgoraKeyMetricsPageContent } from "@/components/agora-key-metrics";

export const metadata: Metadata = {
  title: "声网核心数据 | Agora Equity Research",
  description: "声网季度核心数据。",
};

export default function AgoraKeyMetricsPage() {
  return <AgoraKeyMetricsPageContent />;
}
