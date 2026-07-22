---
name: twilio-npm-dashboard-update
description: Refresh and validate the Twilio npm data used by the Agora Research developer downloads dashboard.
---

# Twilio npm data update

Track only `@twilio/voice-sdk` and `twilio`.

1. Check `git status -sb` and preserve unrelated changes.
2. Run `python scripts/build_vendor_npm_dashboards.py` from the repository root.
3. Validate `public/data/dev-npm-downloads/Data/twilio_npm_weekly_downloads.csv` and `public/data/dev-npm-downloads/json/twilio_npm_downloads_metadata.json`.
4. Confirm the CSV header matches the two packages and metadata contains `source.latest_complete_week_start`.
5. Validate `/Demand/Dev_npm_downloads/`; do not generate Bandwidth data or a standalone HTML page.
6. Commit and push only when the user requests publication.

Never hand-edit download counts. Network access may require escalation.
