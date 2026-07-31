---
name: livekit-npm-dashboard-update
description: Refresh and validate the LiveKit npm data used by the Agora Research developer downloads dashboard.
---

# LiveKit npm data update

Track `livekit-client`, `@livekit/components-react`, `@livekit/react-native`, `@livekit/agents`, and `@livekit/agents-plugin-silero`.

1. Check `git status -sb` and preserve unrelated changes.
2. Run `python scripts/build_livekit_npm_dashboard.py` from the repository root.
3. Validate `public/data/dev-npm-downloads/Data/livekit_npm_weekly_downloads.csv` and `public/data/dev-npm-downloads/json/livekit_npm_downloads_metadata.json`.
4. Confirm the CSV header matches the five packages and metadata contains `source.latest_complete_week_start`.
5. Validate `/Demand/Dev_npm_downloads/`; do not generate a standalone HTML page.
6. Commit and push only when the user requests publication.

Never hand-edit download counts. Network access may require escalation.
