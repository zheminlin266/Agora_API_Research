---
name: livekit-npm-dashboard-update
description: Refresh and validate the LiveKit npm CSV and metadata used by the Agora_API_Research single-page dashboard.
---

# LiveKit npm data update

Track `livekit-client`, `@livekit/components-react`, `@livekit/react-native`, `@livekit/agents`, and `@livekit/agents-plugin-silero`.

1. Check `git status -sb` and preserve unrelated changes.
2. Run `python scripts/build_livekit_npm_dashboard.py` from the repository root.
3. Validate `Data/livekit_npm_weekly_downloads.csv` and `json/livekit_npm_downloads_metadata.json`.
4. Confirm the CSV header matches the five packages and metadata contains `source.latest_complete_week_start`.
5. Validate the root `index.html`; do not generate or look for a child HTML page.
6. Commit and push only when the user requests publication.

Never hand-edit download counts. Network access may require escalation.
