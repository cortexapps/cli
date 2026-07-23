---
name: cli-release
description: Use before creating any commit intended for release — determines correct version bump, ensures commit prefix is right, and walks through the release flow. Triggers on "release", "bump version", "merge to staging", "merge to main", "create a release", "what version will this be", or any PR from a feature branch to staging or main.
---

# CLI Release Skill

Use this skill **before writing the commit message** for any change headed to production.
Getting the prefix wrong means the wrong version ships — and fixing it requires an amended force-push.

---

## Step 1: Determine the correct version bump

1. Check the current published tag:
   ```bash
   git fetch origin --tags
   git describe --tags --abbrev=0
   ```

2. Examine commits since that tag on your branch:
   ```bash
   git log <last-tag>..HEAD --oneline
   ```

3. Apply the bump rules (highest wins):
   | Commit prefix | Bump |
   |---|---|
   | `feat:` | **minor** — X.(Y+1).0 |
   | `fix:` | **patch** — X.Y.(Z+1) |
   | `chore:`, `docs:`, other | no bump (don't use for deliverable changes) |

4. **State the expected version out loud** before any commit:
   > "This will produce **1.20.1** because all commits use `fix:` (no `feat:`)."

---

## Step 2: Craft the commit message

- Use `fix:` for bug fixes, `feat:` for new features.
- If the prefix and bump disagree, add an explicit keyword override:
  - `#patch` — force patch regardless of prefix
  - `#minor` — force minor regardless of prefix
  - `#major` — force major (rare)
- **Only use `feat:`/`fix:` for commits that touch deliverable paths**: `cortexapps_cli/`, `pyproject.toml`, `poetry.lock`, `tests/`, `docker/`. Use `chore:` for anything else.

Example:
```
fix: two-pass re-import for catalog entities with x-cortex-relationships #patch
```

---

## Step 3: Choose the release path

**Two valid paths — pick based on whether you're batching fixes:**

### Option A: Feature → main directly (single fix, ship now)
Use this for most fixes. CI runs, tests pass, PR auto-merges, publish fires.

```bash
gh pr create --base main --head <feature-branch> --title "fix: <description>"
```

- `test-pr.yml` runs tests and auto-merges when they pass.
- `publish.yml` triggers on the resulting push to `main`.
- The workflow auto-syncs HISTORY.md back to `staging` after publish.

### Option B: Feature → staging → main (batching multiple fixes)
Use this when you want to collect several fixes before cutting a release.

```bash
# Step 1: land feature on staging (tests run + automerge)
gh pr create --base staging --head <feature-branch> --title "fix: <description>"
# Step 2: when ready to release, merge staging → main (triggers publish)
gh pr create --base main --head staging --title "Release X.Y.Z: <description>"
```

---

## Human review (when needed)

By default, PRs auto-merge when tests pass. When you need a human to review first:

1. Open the PR as a **draft** — tests run for fast feedback, but automerge is skipped.
2. Share for review. Reviewer approves while still in draft.
3. Convert to ready (`gh pr ready <PR_NUMBER>`) — tests re-run, automerge fires.

The reviewer approves *before* you convert, so you control the merge timing.

```bash
# Open as draft
gh pr create --draft --base main --head <feature-branch> --title "fix: <description>"

# After reviewer approves, convert to ready
gh pr ready <PR_NUMBER>
```

---

## Step 4: Monitor PR CI and auto-merge (no human in the loop)

CI takes ~5 minutes. Use this polling loop — it waits 5 minutes before the first check, then polls every 60 seconds. This keeps API calls to a minimum.

```bash
echo "Waiting 5 minutes for CI..."; sleep 300
while true; do
  STATUS=$(gh pr checks <PR_NUMBER> 2>/dev/null | awk '{print $2}' | sort -u)
  echo "$(date '+%H:%M:%S') checks: $STATUS"
  if echo "$STATUS" | grep -q "fail"; then
    echo "CI failed — inspect with: gh pr checks <PR_NUMBER>"; break
  fi
  if ! echo "$STATUS" | grep -qE "pending|in_progress|queued"; then
    echo "All checks passed — merging"
    gh pr merge <PR_NUMBER> --merge
    break
  fi
  sleep 60
done
```

**Critically: do NOT add any commits during or after this loop.** The publish workflow auto-commits `chore: update HISTORY.md for main` after merging. That commit is excluded from the `paths:` trigger filter (`HISTORY.md` is not in `cortexapps_cli/**`, `docker/**`, `pyproject.toml`, or `poetry.lock`), so it will **not** trigger a second publish run. Any commit you push that *does* touch those paths will trigger a new, unwanted build.

---

## Step 5: Monitor the publish workflow after merge

The publish workflow runs 5 parallel jobs under the same `GH_TOKEN` PAT:
`pypi` → `pypi-deploy-event`, `docker`, `docker-deploy-event`, `homebrew`

Wait 2 minutes for the workflow to start, then poll:

```bash
echo "Waiting 2 minutes for publish workflow to start..."; sleep 120
while true; do
  gh run list --limit 5 --branch main --json status,conclusion,name,databaseId \
    --jq '.[] | "\(.name) \(.status) \(.conclusion // "running") \(.databaseId)"'
  echo "---"
  DONE=$(gh run list --limit 1 --branch main --json status --jq '.[0].status')
  [ "$DONE" = "completed" ] && break
  sleep 60
done
# Check final result
gh run list --limit 1 --branch main --json conclusion --jq '.[0].conclusion'
```

**If a job fails with a rate limit error — do NOT push a new commit.** Re-run only the failed jobs:
```bash
gh run rerun --failed <run-id>
```

**Confirm the tag was cut after a successful run:**
```bash
git fetch origin --tags && git tag --sort=-version:refname | head -3
```

---

## Step 5: Homebrew dependency caveat

`mislav/bump-homebrew-formula-action` **cannot** update `resource` blocks for Python dependencies.
If `pyproject.toml` or `poetry.lock` changed dependency versions, manually update `cortexapps/homebrew-tap/Formula/cortexapps-cli.rb` resource blocks after release.

---

## Quick-reference: what lives where

| Thing | Location |
|---|---|
| Versioning rules (full reference) | `CLAUDE.md` lines 165–227 |
| Changelog prefixes (`add:`, `change:`, `remove:`) | `CLAUDE.md` lines 219–224 |
| GitHub Actions release workflow | `.github/workflows/publish.yml` |
| Homebrew formula (local copy) | `homebrew/cortexapps-cli.rb` |
| Re-run failed jobs | `gh run rerun --failed <run-id>` |
