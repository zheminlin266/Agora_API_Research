#!/usr/bin/env python3
"""Build RTC competitor npm weekly downloads dashboard.

Tracks Tencent TRTC, ZEGO, Alibaba Cloud RTC, and Volcengine RTC packages.
Uses lib.npm_dashboard shared library.
"""
from __future__ import annotations

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.npm_dashboard import VendorConfig, run

ROOT = Path(__file__).resolve().parent.parent

PACKAGES = [
    "trtc-cloud-js-sdk",
    "zego-express-engine-webrtc",
    "aliyun-rtc-sdk",
    "@volcengine/rtc",
]

COLORS = {
    "trtc-cloud-js-sdk": "#2563eb",
    "zego-express-engine-webrtc": "#dc2626",
    "aliyun-rtc-sdk": "#059669",
    "@volcengine/rtc": "#7c3aed",
}

NOTES = {
    "trtc-cloud-js-sdk": "腾讯 TRTC Web SDK。反映腾讯实时音视频在 Web 端的开发者集成需求。npm 下载量包含 CI 和镜像，适合看趋势。",
    "zego-express-engine-webrtc": "ZEGO 即构 WebRTC 引擎 SDK。反映即构在 Web 端音视频开发者的采用趋势。",
    "aliyun-rtc-sdk": "阿里云 RTC Web SDK。反映阿里云实时音视频在 Web 端的集成需求。",
    "@volcengine/rtc": "火山引擎 RTC Web SDK。反映火山引擎实时音视频在 Web 端的开发者采用情况。",
}

CONFIG = VendorConfig(
    vendor="rtc-competitor",
    display_name="RTC Competitor",
    packages=PACKAGES,
    csv_path=ROOT / "Data" / "rtc_competitor_npm_weekly_downloads.csv",
    html_path=ROOT / "html" / "rtc_competitor_npm_downloads_dashboard.html",
    meta_path=ROOT / "json" / "rtc_competitor_npm_downloads_metadata.json",
    colors=COLORS,
    package_notes=NOTES,
    lang="zh-CN",
    include_latest_version=False,
    user_agent="codex-rtc-competitor-npm-dashboard/1.0",
)


def main() -> None:
    result = run(CONFIG)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
