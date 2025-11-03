# Release Guide

Releases are now driven entirely from Git tags. The process happens in two stages:

1. Prepare a release branch that updates the version and changelog.
2. Merge the branch, then run the GitHub workflow that creates a Sigstore-signed tag. Pushing that tag triggers the publish pipeline.

GitHub Actions handles packaging, publishing, and creating the GitHub release once the tag is pushed.

## Prerequisites

Before creating a release, ensure you have **git-cliff** installed for automatic changelog generation:

```bash
# Install via cargo
cargo install git-cliff

# Or via package manager (macOS)
brew install git-cliff

# Or via package manager (Linux)
# See https://git-cliff.org/docs/installation for your distro
```

## Quick Start

```bash
# 1. Prepare the release branch with version + changelog updates
uv run python scripts/release.py

# 2. After the PR merges (on main), trigger the signed-tag workflow
gh workflow run create-signed-tag.yml --ref main --field version=0.5.2
```

## Stage 1 - Prepare the Release Branch

The default command (`uv run python scripts/release.py`) performs the following:

1. Verifies you are on a clean, up-to-date `main`.
2. Runs the quality gates (pytest, ruff, pyright).
3. Prompts for the new semantic version (suggests the next patch).
4. Updates `pyproject.toml`.
5. Regenerates `uv.lock` so dependencies stay in sync.
6. Uses `git-cliff` to auto-generate `CHANGELOG.md` entries from conventional commits and lets you edit.
7. Creates a branch named `release/vX.Y.Z`.
8. Commits the version + changelog changes.
9. Pushes the release branch to `origin`.

### What you do next

1. Open a pull request from `release/vX.Y.Z` to `main`.
2. Get the PR reviewed and merged.
3. Confirm that `main` now contains the release commit.

> Tip: The script prints the computed version number—use that value when you trigger the signed-tag workflow.

## Stage 2 - Create and Push the Signed Tag

Once the release branch is merged into `main`:

```bash
# Optional: confirm you are on the tip of main
git checkout main
git pull --ff-only

# Trigger the signed tag workflow (replace 0.5.2 with your version)
gh workflow run create-signed-tag.yml --ref main --field version=0.5.2
```

That workflow:

1. Sets up Gitsign for keyless signing using Sigstore.
2. Creates a `vX.Y.Z` cryptographically signed tag on the current `main`.
3. Pushes the tag to `origin`.

The pushed tag triggers the `Publish to PyPI` workflow (`.github/workflows/publish.yml`).

> Tip: the workflow aborts if the tag is already present locally or on the remote, preventing accidental overwrites.

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
