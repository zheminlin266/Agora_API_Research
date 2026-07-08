---
name: livekit-npm-dashboard-update
description: Update LiveKit npm weekly download CSV, dashboard HTML, and metadata JSON for the Agora_API_Research GitHub Pages root. Use when the user asks to refresh LiveKit npm package downloads, regenerate or validate livekit_npm_weekly_downloads.csv, livekit_npm_downloads_dashboard.html, or livekit_npm_downloads_metadata.json, commit, push, or verify the public LiveKit npm dashboard.
---

# LiveKit npm Dashboard Update

## Purpose

Update the LiveKit npm weekly-download dataset and dashboard in `zheminlin266/Agora_API_Research`, repository root.

Tracked packages:

- `livekit-client`
- `@livekit/components-react`
- `@livekit/react-native`
- `@livekit/agents`
- `@livekit/agents-plugin-silero`

## Canonical Locations

- Git repository: `D:\【07】研究\【01】企业和主题研究\51 声网 API\fundamental_research_live`
- Artifact folder: repository root
- Update script: `scripts/build_livekit_npm_dashboard.py`
- CSV: `livekit_npm_weekly_downloads.csv`
- HTML: `livekit_npm_downloads_dashboard.html`
- Metadata: `livekit_npm_downloads_metadata.json`
- Public page: `https://zheminlin266.github.io/Agora_API_Research/livekit_npm_downloads_dashboard.html`

## Workflow

1. Check `git status -sb` from `fundamental_research_live`.
   - Do not stage unrelated user changes.
2. Run from `fundamental_research_live` with the bundled Python runtime:

   ```powershell
   python scripts/build_livekit_npm_dashboard.py
   ```

   The script queries npm registry and npm downloads APIs, then regenerates CSV, HTML, and metadata JSON.
3. Validate outputs.
   - CSV header must be:

     ```text
     week_start,livekit-client,@livekit/components-react,@livekit/react-native,@livekit/agents,@livekit/agents-plugin-silero
     ```

   - Metadata must include `source.latest_download_day`, `source.html_chart_complete_through_week_start`, and `source.html_chart_policy`.
   - `source.html_chart_policy` should say HTML line charts exclude the latest incomplete week while CSV retains all weekly aggregates.
   - HTML must include `LiveKit npm`, all package names, `range-start`, `range-end`, and the latest complete-week marker from metadata.
4. Inspect `git diff --stat`.
5. Commit only these intended files when changed:
   - `livekit_npm_weekly_downloads.csv`
   - `livekit_npm_downloads_dashboard.html`
   - `livekit_npm_downloads_metadata.json`
   - `scripts/build_livekit_npm_dashboard.py` only if intentionally changed
6. Push to `origin main` if a commit was created and the user asked to publish; do not use GitHub Actions for this refresh.
7. Verify the public page returns HTTP 200 and contains all package names plus the latest complete-week marker.


## Weekly Codex Run Policy

- Run data fetches, CSV/dashboard regeneration, validation, commits, and pushes directly in Codex.
- Do not run, trigger, rerun, or depend on GitHub Actions for the weekly dashboard refresh.
- Treat GitHub Pages as read-only verification after `git push`; if it lags, report HTTP status, `Last-Modified`, and raw GitHub `main` evidence instead of attempting an Actions rerun.

## Notes
- Network access may require sandbox escalation.
- Prefer the repository script over ad hoc CSV or HTML editing.
