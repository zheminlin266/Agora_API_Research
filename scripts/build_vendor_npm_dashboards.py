#!/usr/bin/env python3
"""Build Twilio and Bandwidth npm weekly downloads dashboards.

Python replacement for build_vendor_npm_dashboards.mjs.
Uses lib.npm_dashboard shared library.

Usage:
  python build_vendor_npm_dashboards.py              # refresh from npm API
  python build_vendor_npm_dashboards.py --from-existing  # rebuild HTML from existing CSV+JSON
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.npm_dashboard import VendorConfig, run, run_from_existing

ROOT = Path(__file__).resolve().parent.parent

# ── Twilio ─────────────────────────────────────────────────────────────────

TWILIO_PACKAGES = [
    "twilio-video",
    "@twilio/voice-sdk",
    "@twilio/video-react-native-sdk",
    "@twilio/video-processors",
    "twilio",
]

TWILIO_DESCRIPTIONS = {
    "twilio-video": "Twilio Video JavaScript 浏览器端 SDK。",
    "@twilio/voice-sdk": "Twilio JavaScript Voice SDK，用于浏览器和应用内语音通话集成。",
    "@twilio/video-react-native-sdk": "Twilio Video 的 React Native WebRTC SDK。",
    "@twilio/video-processors": "Twilio Video 的 JavaScript 视频处理库，用于背景处理等视频效果。",
    "twilio": "Twilio 通用 Node.js 辅助库，覆盖范围不限于实时音视频 API。",
}

TWILIO_NOTES = {
    "twilio-video": "浏览器视频 SDK 的需求信号，主要对应 Twilio Programmable Video 集成。周度 npm 下载量包含自动化安装，应理解为开发者兴趣，而不是实际使用量。",
    "@twilio/voice-sdk": "JavaScript Voice SDK 的需求信号，反映浏览器和应用内语音通话集成的开发者关注度。观察趋势和版本发布前后的变化比绝对值更重要。",
    "@twilio/video-react-native-sdk": "面向移动端 Twilio Video 集成的 React Native 视频 SDK 信号。序列缺失或读数较低可能来自包生命周期变化，不一定代表产品需求偏弱。",
    "@twilio/video-processors": "用于背景处理等效果的视频预处理包，有助于把附加媒体处理兴趣与核心视频 SDK 需求区分开。",
    "twilio": "Twilio 通用 Node.js 辅助库，覆盖多类 Twilio API，不只代表 RTC；应与视频和语音 SDK 包分开比较。",
}

TWILIO_CONFIG = VendorConfig(
    vendor="twilio",
    display_name="Twilio",
    packages=TWILIO_PACKAGES,
    csv_path=ROOT / "Data" / "twilio_npm_weekly_downloads.csv",
    html_path=ROOT / "html" / "twilio_npm_downloads_dashboard.html",
    meta_path=ROOT / "json" / "twilio_npm_downloads_metadata.json",
    package_descriptions=TWILIO_DESCRIPTIONS,
    package_notes=TWILIO_NOTES,
    lang="zh-CN",
    include_latest_version=False,
    user_agent="codex-vendor-npm-weekly-dashboard/1.0",
)

# ── Bandwidth ──────────────────────────────────────────────────────────────

BANDWIDTH_PACKAGES = [
    "bandwidth-rtc",
    "@bandwidth/bw-webrtc-sdk",
    "bandwidth-sdk",
]

BANDWIDTH_DESCRIPTIONS = {
    "bandwidth-rtc": "BandwidthRTC Node 应用 SDK。",
    "@bandwidth/bw-webrtc-sdk": "Bandwidth WebRTC SDK，用于浏览器实时通信集成。",
    "bandwidth-sdk": "Bandwidth SDK 的 OpenAPI 客户端，覆盖范围可能不限于 WebRTC。",
}

BANDWIDTH_NOTES = {
    "bandwidth-rtc": "Bandwidth RTC 包的需求信号。如果 npm 元数据缺失，看板仍会保留该包并显示未找到状态。",
    "@bandwidth/bw-webrtc-sdk": "Bandwidth WebRTC SDK 包的需求信号，反映浏览器实时通信集成的开发者关注度。",
    "bandwidth-sdk": "Bandwidth 通用 SDK 的需求信号，可能包含非 WebRTC API 使用，因此应与 RTC 专用包分开解读。",
}

BANDWIDTH_CONFIG = VendorConfig(
    vendor="bandwidth",
    display_name="Bandwidth",
    packages=BANDWIDTH_PACKAGES,
    csv_path=ROOT / "Data" / "bandwidth_npm_weekly_downloads.csv",
    html_path=ROOT / "html" / "bandwidth_npm_downloads_dashboard.html",
    meta_path=ROOT / "json" / "bandwidth_npm_downloads_metadata.json",
    package_descriptions=BANDWIDTH_DESCRIPTIONS,
    package_notes=BANDWIDTH_NOTES,
    lang="zh-CN",
    include_latest_version=False,
    user_agent="codex-vendor-npm-weekly-dashboard/1.0",
)

VENDOR_CONFIGS = [TWILIO_CONFIG, BANDWIDTH_CONFIG]


def main() -> None:
    from_existing = "--from-existing" in sys.argv
    results = []
    for config in VENDOR_CONFIGS:
        if from_existing:
            results.append(run_from_existing(config))
        else:
            results.append(run(config))
    print(json.dumps({
        "mode": "from-existing" if from_existing else "refresh",
        "results": results,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
