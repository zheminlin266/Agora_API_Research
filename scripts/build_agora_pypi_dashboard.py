#!/usr/bin/env python3
"""Refresh PyPI data used by the Agora cards on the single-page dashboard."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.pypi_dashboard import PyPIConfig, run_pypi

CONFIG = PyPIConfig(
    vendor="agora",
    packages=["agora-token-builder", "agora-python-server-sdk"],
    csv_path=ROOT / "Data" / "agora_pypi_weekly_downloads.csv",
    meta_path=ROOT / "json" / "agora_pypi_downloads_metadata.json",
    user_agent="codex-agora-pypi-dashboard/2.0",
)

if __name__ == "__main__":
    print(json.dumps(run_pypi(CONFIG), ensure_ascii=False, indent=2))
