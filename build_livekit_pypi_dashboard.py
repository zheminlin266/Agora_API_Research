#!/usr/bin/env python3
"""Build LiveKit PyPI weekly downloads dashboard.

Refactored to use lib.pypi_dashboard shared library.
Data source: ClickPy public ClickHouse + PyPI JSON API.
"""
from __future__ import annotations

import json
from pathlib import Path

from lib.pypi_dashboard import PyPIConfig, run_pypi

ROOT = Path(__file__).resolve().parent

PACKAGES = ["livekit", "livekit-api", "livekit-agents", "livekit-plugins"]

CONFIG = PyPIConfig(
    vendor="livekit",
    display_name="LiveKit",
    packages=PACKAGES,
    csv_path=ROOT / "Data" / "livekit_pypi_weekly_downloads.csv",
    html_path=ROOT / "html" / "livekit_pypi_downloads_dashboard.html",
    meta_path=ROOT / "json" / "livekit_pypi_downloads_metadata.json",
    package_roles={
        "livekit": "Python SDK",
        "livekit-api": "Server API",
        "livekit-agents": "Agents",
        "livekit-plugins": "Plugins",
    },
    package_notes={
        "livekit": "Realtime audio/video/data Python SDK; useful as the broad SDK adoption signal.",
        "livekit-api": "Server API and token generation package; closer to backend deployment activity.",
        "livekit-agents": "Voice/AI agents framework; the key package for LiveKit's AI application momentum.",
        "livekit-plugins": "Small meta/package signal; treat as early-stage noise unless volume becomes sustained.",
    },
    package_colors={
        "livekit": "#126c73",
        "livekit-api": "#a45a2a",
        "livekit-agents": "#5661a6",
        "livekit-plugins": "#805a7a",
    },
    source_note=(
        "PyPI 下载量统计包文件拉取次数，会受到 CI/CD、容器构建、依赖锁定、镜像缓存和自动化安装影响。"
        "它适合做开发者需求和生态热度的方向性指标，不能直接当作客户数、应用数或真实流量。"
    ),
    interpretation=(
        "读图时应把 livekit、livekit-api、livekit-agents 分开看：SDK、服务端 API 和 Agent 框架代表不同接入环节。"
        "三者同时上行通常说明 Python 生态的端到端集成在扩大；plugins 目前体量极小且 PyPI metadata 当前 404，应只作为低权重线索。"
    ),
    user_agent="codex-livekit-pypi-weekly-dashboard/1.0",
)


def main() -> None:
    result = run_pypi(CONFIG)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
