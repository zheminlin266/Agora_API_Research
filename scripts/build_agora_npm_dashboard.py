#!/usr/bin/env python3
"""Refresh npm data used by the Agora cards on the single-page dashboard."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.npm_dashboard import VendorConfig, run

CONFIG = VendorConfig(
    vendor="agora",
    packages=["agora-rtc-sdk-ng", "agora-rtm-sdk", "agora-rtc-react", "react-native-agora"],
    csv_path=ROOT / "Data" / "agora_npm_weekly_downloads.csv",
    meta_path=ROOT / "json" / "agora_npm_downloads_metadata.json",
    user_agent="codex-agora-npm-dashboard/2.0",
)

if __name__ == "__main__":
    print(json.dumps(run(CONFIG), ensure_ascii=False, indent=2))
