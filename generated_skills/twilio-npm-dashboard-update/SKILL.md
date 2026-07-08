---
name: twilio-npm-dashboard-update
description: Update Twilio npm weekly download CSV, dashboard HTML, and metadata JSON for the Agora_API_Research GitHub Pages root. Use when the user asks to refresh Twilio npm package downloads, regenerate or validate twilio_npm_weekly_downloads.csv, twilio_npm_downloads_dashboard.html, or twilio_npm_downloads_metadata.json, commit, push, or verify the public Twilio npm dashboard.
---

# Twilio npm Dashboard Update

## Purpose

Update the Twilio npm weekly-download dataset and dashboard in `zheminlin266/Agora_API_Research`, repository root.

Tracked packages:

- `twilio-video`
- `@twilio/voice-sdk`
- `@twilio/video-react-native-sdk`
- `@twilio/video-processors`
- `twilio`

## Canonical Locations

- Git repository: `D:\【07】研究\【01】企业和主题研究\51 声网 API\fundamental_research_live`
- Artifact folder: repository root
- Shared update script: `scripts/build_vendor_npm_dashboards.py`
- CSV: `twilio_npm_weekly_downloads.csv`
- HTML: `twilio_npm_downloads_dashboard.html`
- Metadata: `twilio_npm_downloads_metadata.json`
- Public page: `https://zheminlin266.github.io/Agora_API_Research/twilio_npm_downloads_dashboard.html`

## Workflow

1. Check `git status -sb` from `fundamental_research_live`.
   - Do not stage unrelated user changes.
2. Run from `fundamental_research_live` with Python:

   ```powershell
   python scripts/build_vendor_npm_dashboards.py
   ```

   The script refreshes both Twilio and Bandwidth npm dashboards because they share one vendor script.
3. If only rebuilding HTML from existing CSV/metadata is needed, run:

   ```powershell
   python scripts/build_vendor_npm_dashboards.py --from-existing
   ```

4. Validate Twilio outputs.
   - CSV header must be:

     ```text
     week_start,twilio-video,@twilio/voice-sdk,@twilio/video-react-native-sdk,@twilio/video-processors,twilio
     ```

   - Metadata must include `source.latest_download_day`, `source.html_chart_complete_through_week_start`, and `source.html_chart_policy`.
   - HTML must include `Twilio`, all package names, `range-start`, `range-end`, and the latest complete-week marker from metadata.
5. Inspect `git diff --stat`.
6. If the user asked only for Twilio, stage only:
   - `twilio_npm_weekly_downloads.csv`
   - `twilio_npm_downloads_dashboard.html`
   - `twilio_npm_downloads_metadata.json`
   - `scripts/build_vendor_npm_dashboards.py` only if intentionally changed
7. Leave Bandwidth file changes unstaged unless the user requested a multi-vendor refresh.
8. Push to `origin main` if a commit was created and the user asked to publish; do not use GitHub Actions for this refresh.
9. Verify the public page returns HTTP 200 and contains all package names plus the latest complete-week marker.


## Weekly Codex Run Policy

- Run data fetches, CSV/dashboard regeneration, validation, commits, and pushes directly in Codex.
- Do not run, trigger, rerun, or depend on GitHub Actions for the weekly dashboard refresh.
- Treat GitHub Pages as read-only verification after `git push`; if it lags, report HTTP status, `Last-Modified`, and raw GitHub `main` evidence instead of attempting an Actions rerun.

## Notes
- Network access may require sandbox escalation.
- npm download counts include automation, mirrors, robots, cache effects, and dependency installs.
