# Backup, recovery, and Git rollback

This document describes recoverable operations for the repository. It is intentionally conservative: restore into a new directory, never overwrite the only working copy, and never use `git reset --hard` or `git clean -fdx` as a backup strategy.

## Before a refactor or data refresh

1. Stop local dev servers and automated refresh scripts.
2. Record `git status --porcelain=v2`, `git branch -vv`, `git worktree list`, remote URLs, submodule status, and the current `HEAD`.
3. Create a timestamped backup directory outside the repository, preferably on encrypted storage.
4. Copy the full working tree, including tracked, untracked, ignored research files, `.git`, `.vercel`, and submodule contents. Exclude only reproducible `node_modules/` and `.next/`; do not use `robocopy /MIR`.
5. Save `git diff --binary` and `git diff --cached --binary` patches, a `git bundle` verified with `git bundle verify`, an untracked-file list plus independent copies, and SHA-256 hashes for the backup artifacts.
6. Save a separate bundle and status record for `Resources/audio_video_streaming`; a superproject bundle does not contain submodule objects.

Never place `.env*`, tokens, or credentials in Git or an unencrypted backup. Store secrets only in the approved password manager or encrypted backup.

## Establishing a clean feature worktree

Fetch before creating a feature branch and verify that the fetched commit is the expected GitHub `main`:

```powershell
git fetch --prune origin
git rev-parse origin/main
git ls-remote origin refs/heads/main
git worktree add -b codex/<scope>-<timestamp> ..\Agora_API_Research_<scope> origin/main
git -C ..\Agora_API_Research_<scope> submodule update --init --recursive
git -C ..\Agora_API_Research_<scope> status --short
```

The local `main`, `origin/main`, and GitHub `refs/heads/main` should point to the same SHA before release. Keep a dirty rescue worktree on its backup branch; do not clean it merely to make `git status` look tidy.

## Restoring a snapshot or bundle

Always restore to a new directory:

```powershell
git clone <path-to-superproject.bundle> Agora_API_Research_restore_<timestamp>
git -C Agora_API_Research_restore_<timestamp> fsck --full
git -C Agora_API_Research_restore_<timestamp> checkout <recorded-head-sha>
git -C Agora_API_Research_restore_<timestamp> apply --check <staged.patch>
git -C Agora_API_Research_restore_<timestamp> apply --check <unstaged.patch>
```

Apply staged and unstaged patches only after the checks succeed, then copy the independently backed-up untracked files into the new directory. Restore the submodule from its own bundle and recorded gitlink SHA. Compare status, refs, hashes, tests, data validation, and production build before treating the new directory as recovered.

## Rollback

- An unmerged PR is rolled back by closing the PR; retain its branch, worktree, and backup.
- A merged code regression is reverted with a new branch and `git revert <merge-sha>`, followed by the normal CI/Preview/PR process. Do not reset or force-push `main`.
- For a production incident, a Vercel alias may be temporarily rolled back to the previous Ready deployment only with explicit authorization. Open a Git revert or fix-forward PR immediately, and restore deployment SHA = `main` SHA when the fix is Ready.
- For an incorrect data refresh, revert the generator and its generated CSV/metadata together. Never repair production files manually.

Keep the rescue branch, feature worktree, and verified backup until production has passed two consecutive checks or for at least 30 days. Deleting them is a separate destructive operation requiring explicit approval.

## Release consistency check

Before declaring a release complete, verify:

1. GitHub `main`, local `main`, and `origin/main` are identical.
2. The merged commit has passing CI and a Ready Vercel deployment.
3. The production alias points to that deployment.
4. Home, search, an article page, the download dashboard, and the metrics page pass smoke checks.
