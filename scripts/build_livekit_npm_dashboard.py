#!/usr/bin/env python3
"""Build LiveKit npm weekly downloads dashboard.

Refactored to use lib.npm_dashboard shared library.
Config: 5 npm packages, no derived columns.
"""
from __future__ import annotations

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.npm_dashboard import (
    SectionGroup, VendorConfig, run,
)

ROOT = Path(__file__).resolve().parent.parent

PACKAGES = [
    "livekit-client",
    "@livekit/components-react",
    "@livekit/react-native",
    "@livekit/agents",
    "@livekit/agents-plugin-silero",
]

COLORS = {
    "livekit-client": "#2563eb",
    "@livekit/components-react": "#059669",
    "@livekit/react-native": "#dc2626",
    "@livekit/agents": "#7c3aed",
    "@livekit/agents-plugin-silero": "#c2410c",
}

NOTES = {
    "livekit-client": "功能：面向浏览器和 Node 环境 LiveKit 应用的核心 JavaScript client SDK。它是所选包中最宽口径的开发者需求信号。",
    "@livekit/components-react": "功能：用于构建 LiveKit 视频、音频和房间 UI 的 React 组件层。它反映基于 client SDK 之上的高层 React 采用情况。",
    "@livekit/react-native": "功能：面向移动端 LiveKit 应用的 React Native SDK。它适合观察跨平台移动集成需求。",
    "@livekit/agents": "功能：JavaScript/TypeScript LiveKit Agents 框架包，面向实时 AI agent、语音工作流和服务端 agent 应用。",
    "@livekit/agents-plugin-silero": "功能：LiveKit Agents 的 Silero 语音活动检测插件。它是更窄口径的 AI agent 生态信号，应与 @livekit/agents 一起观察。",
}

CONFIG = VendorConfig(
    vendor="livekit",
    display_name="LiveKit",
    packages=PACKAGES,
    csv_path=ROOT / "Data" / "livekit_npm_weekly_downloads.csv",
    html_path=ROOT / "html" / "livekit_npm_downloads_dashboard.html",
    meta_path=ROOT / "json" / "livekit_npm_downloads_metadata.json",
    colors=COLORS,
    package_notes=NOTES,
    section_groups=[
        SectionGroup(
            title="Client SDKs",
            subtitle="Browser, React, and React Native packages.",
            packages=PACKAGES[:3],
        ),
        SectionGroup(
            title="Agents And Voice AI",
            subtitle="Agent framework and Silero voice activity detection plugin.",
            packages=PACKAGES[3:],
        ),
    ],
    lang="zh-CN",
    include_latest_version=True,
    user_agent="codex-livekit-npm-weekly-dashboard/1.0",
)


def main() -> None:
    result = run(CONFIG)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
