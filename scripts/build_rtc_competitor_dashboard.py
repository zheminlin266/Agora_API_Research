#!/usr/bin/env python3
"""Refresh the Tencent TRTC npm series used by the single-page dashboard."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.npm_dashboard import VendorConfig, run

CONFIG = VendorConfig(
    vendor="tencent",
    packages=["trtc-cloud-js-sdk"],
    csv_path=ROOT / "public" / "data" / "dev-npm-downloads" / "Data" / "rtc_competitor_npm_weekly_downloads.csv",
    meta_path=ROOT / "public" / "data" / "dev-npm-downloads" / "json" / "rtc_competitor_npm_downloads_metadata.json",
    user_agent="codex-rtc-competitor-dashboard/2.0",
)

if __name__ == "__main__":
    print(json.dumps(run(CONFIG), ensure_ascii=False, indent=2))
