---
name: livekit-pypi-dashboard-update
description: Update LiveKit PyPI weekly download CSV, dashboard HTML, and metadata JSON for the Agora_API_Research GitHub Pages root. Use when the user asks to refresh LiveKit PyPI package downloads, regenerate or validate livekit_pypi_weekly_downloads.csv, livekit_pypi_downloads_dashboard.html, or livekit_pypi_downloads_metadata.json, commit, push, or verify the public LiveKit PyPI dashboard.
---

# LiveKit PyPI Dashboard Update

## Purpose

Update the LiveKit PyPI weekly-download dataset and dashboard in `zheminlin266/Agora_API_Research`, repository root.

Tracked packages:

- `livekit`
- `livekit-api`
- `livekit-agents`
- `livekit-plugins`

## Canonical Locations

- Git repository: `D:\【07】研究\【01】企业和主题研究\51 声网 API\fundamental_research_live`
- Artifact folder: repository root
- Update script: `build_livekit_pypi_dashboard.py`
- Shared page builder: `build_pypi_dashboard_pages.py`
- CSV: `livekit_pypi_weekly_downloads.csv`
- HTML: `livekit_pypi_downloads_dashboard.html`
- Metadata: `livekit_pypi_downloads_metadata.json`
- Public page: `https://zheminlin266.github.io/Agora_API_Research/livekit_pypi_downloads_dashboard.html`

## Workflow

1. Check `git status -sb` from `fundamental_research_live`.
   - Do not stage unrelated user changes.
2. Run from `fundamental_research_live` with the bundled Python runtime:

   ```powershell
   python build_livekit_pypi_dashboard.py
   ```

   The script queries ClickPy public ClickHouse and PyPI JSON metadata, then regenerates CSV, metadata, and HTML.
3. If only the HTML shell needs rebuilding from existing CSV files, run:

   ```powershell
   python build_pypi_dashboard_pages.py
   ```

   This rebuilds both Agora and LiveKit PyPI HTML pages; stage only the requested artifacts unless the user requested both.
4. Validate outputs.
   - CSV header must be:

     ```text
     week_start,livekit,livekit-api,livekit-agents,livekit-plugins
     ```

   - Missing package/week cells must be `0`.
   - Metadata `dataset.latest_complete_week_start` must exist and be present in the HTML.
   - HTML must include all package names, `range-start`, and the latest complete-week marker.
5. Inspect `git diff --stat`.
6. Commit only these intended files when changed:
   - `livekit_pypi_weekly_downloads.csv`
   - `livekit_pypi_downloads_dashboard.html`
   - `livekit_pypi_downloads_metadata.json`
   - `build_livekit_pypi_dashboard.py` only if intentionally changed
   - `build_pypi_dashboard_pages.py` only if intentionally changed
7. Push to `origin main` if a commit was created and the user asked to publish; do not use GitHub Actions for this refresh.
8. Verify the public page returns HTTP 200 and contains all package names plus the latest complete-week marker.


## Weekly Codex Run Policy

- Run data fetches, CSV/dashboard regeneration, validation, commits, and pushes directly in Codex.
- Do not run, trigger, rerun, or depend on GitHub Actions for the weekly dashboard refresh.
- Treat GitHub Pages as read-only verification after `git push`; if it lags, report HTTP status, `Last-Modified`, and raw GitHub `main` evidence instead of attempting an Actions rerun.

## Notes
- Network access may require sandbox escalation.
- `livekit-plugins` can have metadata anomalies; preserve the package column unless the user explicitly changes the tracking list.
