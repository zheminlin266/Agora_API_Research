# Agora API Research

## Dashboard Links

- [Index](https://zheminlin266.github.io/Agora_API_Research/): dashboard entry page.
- [Agora npm downloads dashboard](https://zheminlin266.github.io/Agora_API_Research/html/agora_npm_downloads_dashboard.html): weekly npm downloads for Agora JavaScript, React, React Native, RTM, and agent-related packages.
- [Agora PyPI downloads dashboard](https://zheminlin266.github.io/Agora_API_Research/html/agora_pypi_weekly_downloads_dashboard.html): weekly PyPI downloads for Agora Python ecosystem packages.
- [LiveKit npm downloads dashboard](https://zheminlin266.github.io/Agora_API_Research/html/livekit_npm_downloads_dashboard.html): weekly npm downloads for LiveKit client, React, React Native, and Agents packages.
- [LiveKit PyPI downloads dashboard](https://zheminlin266.github.io/Agora_API_Research/html/livekit_pypi_downloads_dashboard.html): weekly PyPI downloads for LiveKit Python SDK, server API, Agents, and plugin packages.
- [Twilio npm downloads dashboard](https://zheminlin266.github.io/Agora_API_Research/html/twilio_npm_downloads_dashboard.html): weekly npm downloads for Twilio video, voice, React Native video, video processors, and general SDK packages.
- [Bandwidth npm downloads dashboard](https://zheminlin266.github.io/Agora_API_Research/html/bandwidth_npm_downloads_dashboard.html): weekly npm downloads for Bandwidth RTC, WebRTC, and general SDK packages.
- [RTC competitor npm downloads dashboard](https://zheminlin266.github.io/Agora_API_Research/html/rtc_competitor_npm_downloads_dashboard.html): weekly npm download trends for RTC competitor packages.

## Repository Layout

- `lib/`: shared Python library for npm dashboard data fetching, aggregation, and HTML generation.
- `Data/`: CSV source datasets.
- `html/`: dashboard HTML pages. The root `index.html` stays at the repository root for GitHub Pages.
- `json/`: dashboard metadata JSON files.
- `generated_skills/`: agent skill definitions for automated dashboard updates.
- `workflow.md`: scheduled update workflow for regenerating, validating, organizing, and publishing dashboard artifacts.