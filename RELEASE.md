# Release Guide

This guide documents the complete release process for miniflux-tui-py. The process uses git-cliff for changelog generation, Sigstore for cryptographic signing, and automated PyPI publishing via GitHub Actions.

## Prerequisites

### Required Tools

1. **git-cliff** - Automatic changelog generation from conventional commits

```bash
# macOS
brew install git-cliff

# Linux (Cargo)
cargo install git-cliff

# See https://git-cliff.org/docs/installation for other options
```

2. **GitHub CLI** - For triggering workflows

```bash
# macOS
brew install gh

# Linux
# See https://cli.github.com/manual/installation
```

3. **uv** - Python package manager (should already be installed for development)

## Release Process Overview

The release process has **THREE critical stages** that must be completed in order:

1. **Stage 1**: Prepare release PR (version bump + changelog)
2. **Stage 2**: Merge the PR to main (**REQUIRED** - don't skip!)
3. **Stage 3**: Manually push the tag to trigger publish workflow

⚠️ **CRITICAL**: You must merge the release PR before creating the tag, or the build will use the wrong version!

## Stage 1: Prepare Release PR

Run the release script from a clean main branch:

```bash
# Ensure you're on main and up-to-date
git checkout main
git pull --ff-only

# Run the release preparation script
uv run scripts/release.py
```

The script will:
1. ✅ Verify you're on a clean, up-to-date `main`
2. ✅ Run quality gates (pytest, ruff, pyright)
3. ✅ Prompt for the new semantic version (suggests next patch)
4. ✅ Update `pyproject.toml` with new version
5. ✅ Regenerate `uv.lock` to keep dependencies in sync
6. ✅ Use `git-cliff` to auto-generate `CHANGELOG.md` from commits
7. ✅ Open your `$EDITOR` to review/edit the changelog
8. ✅ Create a branch named `release/vX.Y.Z`
9. ✅ Commit version + changelog changes
10. ✅ Push the release branch to origin

**Action Required**: The script will print a URL to create a pull request. Open that URL and create the PR.

## Stage 2: Merge Release PR ⚠️ DO NOT SKIP

**This step is CRITICAL!** The release PR must be merged to main before creating the tag.

```bash
# Wait for CI to pass on the PR, then merge it
gh pr merge <PR-NUMBER> --squash  # or merge via GitHub UI

# After merge, update your local main
git checkout main
git pull --ff-only

# VERIFY the version is correct in main
grep "^version" pyproject.toml
# Should show: version = "X.Y.Z" (your new version)
```

If you skip this step, the build will use the old version from main and upload the wrong version to PyPI!

## Stage 3: Create Tag and Trigger Publish

⚠️ **Important**: The GitHub Actions `create-signed-tag` workflow **CANNOT** trigger the publish workflow due to GitHub's security restrictions (GITHUB_TOKEN doesn't trigger other workflows). You must manually push the tag.

### Option A: Manual Tag Push (Recommended)

```bash
# Ensure you're on the updated main branch
git checkout main
git pull --ff-only

# Create and push the signed tag locally
git tag -s v0.5.3 -m "v0.5.3"
git push origin v0.5.3
```

### Option B: Use Workflow Then Manual Push

```bash
# First, trigger the workflow to create the signed tag
gh workflow run create-signed-tag.yml --ref main --field version=0.5.3

# Wait 30 seconds for it to complete, then manually push
sleep 30
git fetch --tags
git push origin v0.5.3
```

The manual push triggers the `Publish to PyPI` workflow which will:
- ✅ Build distribution packages (wheel + sdist)
- ✅ Publish to PyPI via Trusted Publisher (OIDC)
- ✅ Create binaries for Linux, macOS, Windows
- ✅ Generate SBOMs (CycloneDX + SPDX)
- ✅ Create GitHub Release with all artifacts
- ✅ Generate build attestations

## Monitoring Release Progress

### Check Workflow Status

```bash
# List recent workflow runs
gh run list --limit 5

# Watch a specific run
gh run watch <RUN-ID>

# View run details
gh run view <RUN-ID>
```

### Verify PyPI Publication

```bash
# Check latest version on PyPI
curl -s https://pypi.org/pypi/miniflux-tui-py/json | jq -r '.info.version'

# Or visit: https://pypi.org/project/miniflux-tui-py/
```

### Verify GitHub Release

```bash
# List releases
gh release list --limit 5

# View specific release
gh release view v0.5.3

# Or visit: https://github.com/reuteras/miniflux-tui-py/releases
```

## Troubleshooting

### Problem: Publish workflow didn't trigger after creating tag

**Cause**: GitHub Actions using `GITHUB_TOKEN` don't trigger other workflows (security feature).

**Solution**: Manually push the tag from your local machine:

```bash
git fetch --tags
git push origin vX.Y.Z
```

### Problem: Wrong version published to PyPI

**Cause**: You created the tag before merging the release PR, so main still had the old version.

**Solution**:
1. Delete the incorrect tag and release
2. Merge the release PR
3. Create the tag again

```bash
# Delete tag locally and remotely
git tag -d vX.Y.Z
git push origin :vX.Y.Z

# Delete GitHub release
gh release delete vX.Y.Z

# Merge release PR
gh pr merge <PR-NUMBER> --squash

# Update main and verify version
git checkout main
git pull --ff-only
grep "^version" pyproject.toml

# Create tag again
git tag -s vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

### Problem: Release is in draft state

**Cause**: The release workflow creates drafts by default.

**Solution**: Publish the release manually:

```bash
gh release edit vX.Y.Z --draft=false
```

Or publish via GitHub UI: https://github.com/reuteras/miniflux-tui-py/releases

### Problem: git-cliff fails with template errors

**Cause**: The cliff.toml configuration has syntax errors.

**Solution**: Test git-cliff locally before running release script:

```bash
git-cliff --config cliff.toml --tag 0.5.3 --unreleased
```

## Complete Release Checklist

Use this checklist to ensure you don't miss any steps:

- [ ] Install git-cliff (`brew install git-cliff`)
- [ ] Checkout main and pull latest (`git checkout main && git pull`)
- [ ] Run release script (`uv run scripts/release.py`)
- [ ] Review and edit generated changelog
- [ ] Create PR from the release branch
- [ ] **Wait for CI to pass on the PR**
- [ ] **Merge the release PR** ⚠️ CRITICAL STEP
- [ ] Update local main (`git checkout main && git pull`)
- [ ] **Verify version in pyproject.toml** (`grep "^version" pyproject.toml`)
- [ ] Create and push tag (`git tag -s vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z`)
- [ ] Wait for publish workflow to complete (~3 minutes)
- [ ] Verify PyPI has new version
- [ ] Verify GitHub release exists
- [ ] If release is draft, publish it (`gh release edit vX.Y.Z --draft=false`)
- [ ] Test installation: `pip install miniflux-tui-py --upgrade`

## Release Timeline

Typical release timeline:

1. **Stage 1** (5-10 min): Run release script, create PR
2. **Stage 2** (2-5 min): CI passes, merge PR
3. **Stage 3** (3-5 min): Push tag, publish workflow completes

**Total**: ~10-20 minutes from start to PyPI publication

## Keyless Signing with Sigstore

The release workflow uses **Sigstore Gitsign** for keyless cryptographic signing. This provides:

- ✅ **No long-lived secrets** - Uses short-lived OIDC tokens (valid only during workflow execution)
- ✅ **Automatic transparency log** - All signatures are logged in Sigstore's public transparency log
- ✅ **Consistent security** - Aligns with existing Cosign usage for artifact signing
- ✅ **Reduced attack surface** - No private keys to rotate or store in secrets

### Prerequisites

1. The workflow requires `id-token: write` permission (already configured)
2. GitHub automatically provides OIDC tokens to workflows
3. Gitsign detects these tokens and generates signing certificates via Fulcio

### Verifying Signed Tags

To verify a Gitsign-signed tag:

```bash
# Verify tag signature
git verify-tag v0.5.2

# View signature details
git show --show-signature v0.5.2
```

All signatures are publicly logged in the [Sigstore Rekor transparency log](https://rekor.sigstore.dev/).

## What GitHub Actions Handles

Triggered by a `v*.*.*` tag, the workflow:

1. **Build job**
    - Checks out the repository
    - Runs ruff, pyright, and pytest
    - Builds the source distribution and wheel with `uv build`
2. **Publish job**
    - Publishes the distributions to PyPI using the Trusted Publisher integration
3. **Binaries job**
    - Builds standalone executables for Linux, macOS, and Windows
    - Uploads the binary archives as artifacts
4. **Release job**
    - Downloads all artifacts
    - Generates SBOMs (CycloneDX and SPDX) via Syft
    - Attaches distributions, binaries, and SBOMs to the GitHub release
    - Generates build attestations

Monitor progress at <https://github.com/reuteras/miniflux-tui-py/actions>.

## PyPI Trusted Publisher Setup (One-Time)

Ensure PyPI trusts the workflow before your first tag-triggered release:

1. Visit <https://pypi.org/account/publishing/>.
2. Add a trusted publisher with:
    - **Project:** `miniflux-tui-py`
    - **Repository owner:** `reuteras`
    - **Repository name:** `miniflux-tui-py`
    - **Workflow filename:** `publish.yml`
    - **Environment:** `pypi`

## Fallback / Manual Steps

- If the signed-tag workflow fails in GitHub Actions, press "Re-run all jobs" or:
  ```bash
  gh run rerun <run-id>
  ```
- To create a tag locally in an emergency (only if the workflow is unavailable):
  ```bash
  git checkout main
  git pull --ff-only
  git tag -s vX.Y.Z -m "vX.Y.Z"
  git push origin vX.Y.Z
  ```
  **Note:** Local tags will use your personal signing key (SSH or GPG) rather than Gitsign. This is acceptable for emergency releases, but prefer the automated workflow for consistent provenance.

The publish workflow can be re-run from the GitHub Actions UI if needed.
