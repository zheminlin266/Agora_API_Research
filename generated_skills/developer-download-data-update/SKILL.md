---
name: developer-download-data-update
description: Refresh, validate, and maintain the unified developer download dashboard in Agora_Research. Use when updating npm or PyPI download data, rebuilding the dashboard data contract, checking the Dev_npm_downloads page, or preparing its PR preview.
---

# Developer Download Data Update

Refresh the six datasets behind `/Demand/Dev_npm_downloads/` through the
repository's single updater. Preserve unrelated work, never hand-edit
generated data, and keep CSV, metadata, and manifest changes consistent.

## Update workflow

1. From the repository root, inspect `git status -sb`. Do not stage unrelated files.
2. Use the unified updater:

   ```powershell
   python scripts/update_dashboard_data.py
   ```

   This performs an incremental refresh of all six datasets:
   `agoraNpm`, `agoraPypi`, `livekitNpm`, `livekitPypi`, `twilioNpm`, and `rtcNpm`.
3. For a full historical rebuild, use:

   ```powershell
   python scripts/update_dashboard_data.py --rebuild
   ```
4. To update only selected datasets, repeat `--dataset`, for example:

   ```powershell
   python scripts/update_dashboard_data.py --dataset agoraNpm --dataset agoraPypi
   ```

5. Use `--manifest-only` only when regenerating the frontend manifest without
   contacting upstream sources.

## Validation

Run these checks after a refresh:

```powershell
npm.cmd run validate:data
npm.cmd test
npm.cmd run typecheck
npm.cmd run build
```

If dependencies are absent, run `npm.cmd ci` first. Treat validation failures,
empty output, schema changes, row-count collapse, latest-week rollback, and
unexpected historical changes as refresh failures.

The CSV may contain a trailing partial week. Use
`source.latest_complete_week_start` from metadata as the dashboard cutoff; do
not manually remove the partial row. The frontend loads paths and package
mappings from `public/data/dev-npm-downloads/manifest.json`. Do not create or
maintain standalone HTML dashboards.

## Maintenance and publication

Keep dataset definitions in `lib/dashboard_config.py`, fetch and merge logic in
`lib/npm_dashboard.py` and `lib/pypi_dashboard.py`, and safety checks in
`lib/dashboard_outputs.py` and `scripts/validate_dashboard_data.py`. Add or
update tests when changing update semantics. Do not add a scheduler unless
explicitly requested.

When publication is requested, work from a branch based on `origin/main`, stage
only intended code, data, and docs, commit, and push the branch. Open or update
a PR and let its Vercel integration generate the preview. Verify the PR CI and
the `/Demand/Dev_npm_downloads/` preview route before reporting completion.
