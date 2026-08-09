---
name: agora-pypi-dashboard-update
description: Refresh and validate the Agora PyPI data used by the Agora Research developer downloads dashboard.
---

# Agora PyPI data update

Track only `agora-token-builder` and `agora-python-server-sdk`.

1. Check `git status -sb` and preserve unrelated changes.
2. Run `python scripts/update_dashboard_data.py --dataset agoraPypi` from the repository root.
3. Validate `public/data/dev-npm-downloads/Data/agora_pypi_weekly_downloads.csv` and `public/data/dev-npm-downloads/json/agora_pypi_downloads_metadata.json`.
4. Confirm the CSV header matches the two packages and metadata contains `source.latest_complete_week_start`.
5. Validate `/Demand/Dev_npm_downloads/`; do not generate a standalone HTML page.
6. Commit and push only when the user requests publication.

Never hand-edit download counts. Network access may require escalation.
