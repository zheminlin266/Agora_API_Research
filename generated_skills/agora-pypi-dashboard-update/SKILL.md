---
name: agora-pypi-dashboard-update
description: Update Agora PyPI weekly download CSV and dashboard artifacts for the Agora_API_Research GitHub Pages root. Use when the user asks to refresh Agora PyPI package downloads, regenerate or validate agora_pypi_weekly_downloads.csv or agora_pypi_weekly_downloads_dashboard.html, exclude incomplete-week chart points, commit, push, or verify the public Agora PyPI dashboard.
---

# Agora PyPI Dashboard Update

## Purpose

Update the Agora PyPI weekly-download dataset and dashboard in `zheminlin266/Agora_API_Research`, repository root.

Tracked packages:

- `agora-token-builder`
- `agora-python-server-sdk`
- `agora-python-sdk`
- `agora-realtime-ai-api-v1`

## Canonical Locations

- Git repository: `D:\【07】研究\【01】企业和主题研究\51 声网 API\fundamental_research_live`
- Artifact folder: repository root
- CSV: `agora_pypi_weekly_downloads.csv`
- HTML: `agora_pypi_weekly_downloads_dashboard.html`
- Shared page builder: `build_pypi_dashboard_pages.py`
- Skill update script: `scripts/update_agora_pypi_dashboard.py`
- Public page: `https://zheminlin266.github.io/Agora_API_Research/agora_pypi_weekly_downloads_dashboard.html`

## Workflow

1. Check `git status -sb` from `fundamental_research_live`.
   - Do not stage unrelated user changes.
2. Run the skill script with the bundled Python runtime:

   ```powershell
   python <skill-dir>/scripts/update_agora_pypi_dashboard.py --repo <repo-path>
   ```

   The script queries ClickPy public ClickHouse at `https://sql-clickhouse.clickhouse.com/?user=play` and writes the Agora PyPI CSV and HTML dashboard.
3. If only the HTML shell needs rebuilding from the existing CSV, run from the repository root:

   ```powershell
   python build_pypi_dashboard_pages.py
   ```

   This rebuilds both Agora and LiveKit PyPI HTML pages; stage only the requested artifacts unless the user requested both.
4. Validate outputs before committing.
   - CSV header must be:

     ```text
     week_start,agora_token_builder_downloads,agora_python_server_sdk_downloads,agora_python_sdk_downloads,agora_realtime_ai_api_v1_downloads
     ```

   - Week starts must be Monday ISO dates.
   - Missing package/week cells must be `0`.
   - The dashboard may retain the latest partial source week in embedded data, but charts and summary metrics must use the latest complete week.
   - HTML must include all four package names and the latest complete-week marker printed by the update script.
5. Inspect `git diff --stat`.
6. Commit only these intended files when changed:
   - `agora_pypi_weekly_downloads.csv`
   - `agora_pypi_weekly_downloads_dashboard.html`
   - `build_pypi_dashboard_pages.py` only if intentionally changed
7. Push to `origin main` if a commit was created and the user asked to publish; do not use GitHub Actions for this refresh.
8. Verify the public page returns HTTP 200 and contains the latest complete-week marker and package names.


## Weekly Codex Run Policy

- Run data fetches, CSV/dashboard regeneration, validation, commits, and pushes directly in Codex.
- Do not run, trigger, rerun, or depend on GitHub Actions for the weekly dashboard refresh.
- Treat GitHub Pages as read-only verification after `git push`; if it lags, report HTTP status, `Last-Modified`, and raw GitHub `main` evidence instead of attempting an Actions rerun.

## Notes
- Network access may require sandbox escalation.
- The GitHub `tree` or `blob` URL is a code viewer; use the GitHub Pages URL to verify the interactive dashboard.
