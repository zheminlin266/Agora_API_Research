#!/usr/bin/env python3
"""Refresh npm data used by the LiveKit cards on the single-page dashboard."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.npm_dashboard import VendorConfig, run

CONFIG = VendorConfig(
    vendor="livekit",
    packages=[
        "livekit-client",
        "@livekit/components-react",
        "@livekit/react-native",
        "@livekit/agents",
        "@livekit/agents-plugin-silero",
    ],
    csv_path=ROOT / "public" / "data" / "dev-npm-downloads" / "Data" / "livekit_npm_weekly_downloads.csv",
    meta_path=ROOT / "public" / "data" / "dev-npm-downloads" / "json" / "livekit_npm_downloads_metadata.json",
    user_agent="codex-livekit-npm-dashboard/2.0",
)

if __name__ == "__main__":
    print(json.dumps(run(CONFIG), ensure_ascii=False, indent=2))
