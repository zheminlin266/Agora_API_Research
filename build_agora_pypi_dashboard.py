#!/usr/bin/env python3
"""Build Agora PyPI weekly downloads dashboard.

Fetches Agora Python ecosystem package downloads from ClickPy (ClickHouse).
Data source: ClickPy public ClickHouse + PyPI JSON API.
"""
from __future__ import annotations

import json
from pathlib import Path

from lib.pypi_dashboard import PyPIConfig, run_pypi

ROOT = Path(__file__).resolve().parent

PACKAGES = [
    "agora-token-builder",
    "agora-python-server-sdk",
    "agora-python-sdk",
    "agora-realtime-ai-api-v1",
]

CONFIG = PyPIConfig(
    vendor="agora",
    display_name="Agora",
    packages=PACKAGES,
    csv_path=ROOT / "Data" / "agora_pypi_weekly_downloads.csv",
    html_path=ROOT / "html" / "agora_pypi_weekly_downloads_dashboard.html",
    meta_path=ROOT / "json" / "agora_pypi_downloads_metadata.json",
    package_roles={
        "agora-token-builder": "Token Builder",
        "agora-python-server-sdk": "Server SDK",
        "agora-python-sdk": "Python SDK",
        "agora-realtime-ai-api-v1": "Realtime AI",
    },
    package_notes={
        "agora-token-builder": "服务端生成 Agora RTC/RTM token，用于鉴权、频道加入权限和后端接入流程。该包的持续上行通常更接近后端项目开始集成 Agora 鉴权体系的信号。",
        "agora-python-server-sdk": "Python 服务端 SDK，面向房间、用户、录制、REST/服务端 API 等后台管理能力。它更能反映 Python 后端服务把 Agora 能力接入生产或测试环境的需求。",
        "agora-python-sdk": "较早期或通用 Python SDK 包，可能包含历史依赖、测试、自动化脚本和旧项目拉取。该列适合看长期基线和老包残余需求，不适合单独代表新产品采用。",
        "agora-realtime-ai-api-v1": "实时 AI / 语音 AI API 相关包，面向低延迟语音交互、Agent 或实时会话实验。目前基数较小，重点看是否出现连续多周放量，而不是单周波动。",
    },
    package_colors={
        "agora-token-builder": "#126c73",
        "agora-python-server-sdk": "#a45a2a",
        "agora-python-sdk": "#5661a6",
        "agora-realtime-ai-api-v1": "#805a7a",
    },
    source_note=(
        "PyPI 下载量是包文件被 pip、CI/CD、镜像、开发环境或自动化构建拉取的次数。"
        "它更适合观察开发者接入和后端集成需求的方向变化，不应直接等同为唯一开发者、活跃应用或付费客户。"
    ),
    interpretation=(
        "读图时重点看连续数周的趋势和包之间的相对强弱，而不是单周尖峰。"
        "token-builder 更靠近服务端鉴权接入，server-sdk 更靠近 Python 后端调用，python-sdk 带有旧包和测试/自动化噪声，"
        "realtime-ai 包体量小但能提示语音 AI / Agent 方向的早期兴趣。"
    ),
    user_agent="codex-agora-pypi-weekly-dashboard/1.0",
)


def main() -> None:
    result = run_pypi(CONFIG)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
