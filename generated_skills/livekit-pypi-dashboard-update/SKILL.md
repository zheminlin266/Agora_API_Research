---
name: livekit-pypi-dashboard-update
description: Refresh and validate the LiveKit PyPI data used by the Agora Research developer downloads dashboard.
---

# LiveKit PyPI data update

Track only `livekit`, `livekit-api`, and `livekit-agents`.

1. Check `git status -sb` and preserve unrelated changes.
2. Run `python scripts/update_dashboard_data.py --dataset livekitPypi` from the repository root.
3. Validate `public/data/dev-npm-downloads/Data/livekit_pypi_weekly_downloads.csv` and `public/data/dev-npm-downloads/json/livekit_pypi_downloads_metadata.json`.
4. Confirm the CSV header matches the three packages and metadata contains `source.latest_complete_week_start`.
5. Validate `/Demand/Dev_npm_downloads/`; do not generate a standalone HTML page.
6. Commit and push only when the user requests publication.

Never hand-edit download counts. Network access may require escalation.
