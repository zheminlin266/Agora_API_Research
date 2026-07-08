#!/usr/bin/env python3
"""Build Agora npm weekly downloads dashboard.

Refactored to use lib.npm_dashboard shared library.
Config: 9 npm packages + 1 derived column (rtc-sdk-total).
"""
from __future__ import annotations

import json
from pathlib import Path

from lib.npm_dashboard import (
    SectionGroup, VendorConfig, run,
)

ROOT = Path(__file__).resolve().parent

CORE_PACKAGES = [
    "agora-rtc-sdk-ng",
    "agora-rtc-sdk",
    "agora-rtm-sdk",
    "agora-rtc-react",
    "react-native-agora",
]

AI_PACKAGES = [
    "agora-agent-server-sdk",
    "agora-agent-client-toolkit",
    "agora-agent-uikit",
    "agora-conversational-ai-denoiser",
]

PACKAGES = [*CORE_PACKAGES, *AI_PACKAGES]

COLORS = {
    "agora-rtc-sdk-ng": "#2563eb",
    "agora-rtc-sdk": "#d97706",
    "rtc-sdk-total": "#be123c",
    "agora-rtm-sdk": "#b7791f",
    "agora-rtc-react": "#0f766e",
    "react-native-agora": "#7c3aed",
    "agora-agent-server-sdk": "#475569",
    "agora-agent-client-toolkit": "#0891b2",
    "agora-agent-uikit": "#db2777",
    "agora-conversational-ai-denoiser": "#65a30d",
}

NOTES = {
    "agora-rtc-sdk-ng": "功能：Agora WebRTC JavaScript 核心 SDK。它更接近 Web 端音视频通话、直播互动、在线课堂等实际集成需求。下载数包含 CI、镜像和重复安装，不能等同客户数或用量；看趋势、峰值和版本发布后的变化，比看绝对值更可靠。",
    "agora-rtc-sdk": "功能：Agora 旧版 Web RTC JavaScript SDK。它反映 legacy Web 集成、历史项目维护或旧版本依赖需求。数值应与 agora-rtc-sdk-ng 分开看，不能直接相加；若旧包下降而 NG 包上升，通常意味着迁移到新版 SDK。",
    "rtc-sdk-total": "功能：agora-rtc-sdk-ng 与 agora-rtc-sdk 的周度下载合计。它用于观察 Agora Web RTC SDK 总体开发者安装需求，减少新旧包迁移造成的误读；但仍包含 CI、镜像和重复安装，不能代表真实客户数或用量。",
    "agora-rtm-sdk": "功能：Agora Real-Time Messaging 的 JavaScript SDK。它反映实时消息、信令、在线状态、房间控制等互动能力需求。数值可作为 JS 侧 RTM 采用热度，但可能被依赖安装和自动构建放大，适合与 RTC 包趋势交叉判断。",
    "agora-rtc-react": "功能：Agora RTC 的 React 封装。它揭示 React 开发者希望用组件化方式接入实时音视频的需求，更多是前端框架生态信号。它通常会与 Web RTC 核心包重叠，不能简单与 agora-rtc-sdk-ng 相加。",
    "react-native-agora": "功能：Agora RTC 的 React Native SDK。它反映跨平台移动端应用接入语音、视频通话和互动直播的开发需求。下载数包含 CI、镜像和依赖安装，不能等同移动端活跃应用数；更适合观察移动开发者采用趋势。",
    "agora-agent-server-sdk": "功能：Agora Agent 服务端 SDK/兼容包，面向实时语音 Agent、会话控制和服务端集成。它反映开发者在后端接入 Agora Conversational AI/Agent 能力的需求；下载量较小，适合看早期采用趋势。",
    "agora-agent-client-toolkit": "功能：Agora Agent 客户端工具包，用于在前端接入实时语音 Agent、会话状态和交互控制。它反映开发者把 AI Agent 体验嵌入 Web 或应用端的需求，下载量可作为客户端 Agent 集成热度信号。",
    "agora-agent-uikit": "功能：Agora Agent UI Kit，提供构建语音、视频或对话式 AI Agent 界面的组件。它反映开发者希望用现成 UI 快速集成 AI Agent 体验的需求；数值更偏产品化前端组件采用。",
    "agora-conversational-ai-denoiser": "功能：Agora Conversational AI 场景的 Web SDK 降噪扩展。它反映语音 Agent、对话 AI 和实时互动中对语音清晰度、噪声抑制的需求，适合观察 AI 语音体验优化相关采用。",
}

# rtc-sdk-total is derived from the sum of two source packages
DERIVED_COLUMNS = {"rtc-sdk-total": ["agora-rtc-sdk-ng", "agora-rtc-sdk"]}

# Chart series defines both CSV column order and chart display order
CORE_CHART_SERIES = [
    "agora-rtc-sdk-ng",
    "agora-rtc-sdk",
    "rtc-sdk-total",
    "agora-rtm-sdk",
    "agora-rtc-react",
    "react-native-agora",
]
AI_CHART_SERIES = [*AI_PACKAGES]
CHART_SERIES = [*CORE_CHART_SERIES, *AI_CHART_SERIES]

CONFIG = VendorConfig(
    vendor="agora",
    display_name="Agora",
    packages=PACKAGES,
    csv_path=ROOT / "agora_npm_weekly_downloads.csv",
    html_path=ROOT / "agora_npm_downloads_dashboard.html",
    meta_path=ROOT / "agora_npm_downloads_metadata.json",
    colors=COLORS,
    package_notes=NOTES,
    derived_columns=DERIVED_COLUMNS,
    chart_series=CHART_SERIES,
    section_groups=[
        SectionGroup(
            title="Core SDKs",
            subtitle="Web, React, React Native, and messaging packages.",
            packages=CORE_CHART_SERIES,
        ),
        SectionGroup(
            title="AI related",
            subtitle="Agent, conversational AI, and AI voice enhancement packages.",
            packages=AI_PACKAGES,
        ),
    ],
    lang="zh-CN",
    include_latest_version=True,
    user_agent="codex-agora-npm-weekly-dashboard/1.0",
)


def main() -> None:
    result = run(CONFIG)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
