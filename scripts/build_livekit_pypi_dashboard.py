#!/usr/bin/env python3
"""Refresh PyPI data used by the LiveKit cards on the single-page dashboard."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.pypi_dashboard import PyPIConfig, run_pypi

CONFIG = PyPIConfig(
    vendor="livekit",
    packages=["livekit", "livekit-api", "livekit-agents"],
    csv_path=ROOT / "Data" / "livekit_pypi_weekly_downloads.csv",
    meta_path=ROOT / "json" / "livekit_pypi_downloads_metadata.json",
    user_agent="codex-livekit-pypi-dashboard/2.0",
)

if __name__ == "__main__":
    print(json.dumps(run_pypi(CONFIG), ensure_ascii=False, indent=2))
