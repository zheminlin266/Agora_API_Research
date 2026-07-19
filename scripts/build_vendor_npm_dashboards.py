#!/usr/bin/env python3
"""Refresh npm data used by the Twilio cards on the single-page dashboard."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.npm_dashboard import VendorConfig, run

CONFIG = VendorConfig(
    vendor="twilio",
    packages=["@twilio/voice-sdk", "twilio"],
    csv_path=ROOT / "Data" / "twilio_npm_weekly_downloads.csv",
    meta_path=ROOT / "json" / "twilio_npm_downloads_metadata.json",
    user_agent="codex-twilio-npm-dashboard/2.0",
)

if __name__ == "__main__":
    print(json.dumps(run(CONFIG), ensure_ascii=False, indent=2))
