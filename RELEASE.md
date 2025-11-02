# Release Guide

Releases are now driven entirely from Git tags. The process happens in two stages:

1. Prepare a release branch that updates the version and changelog.
2. Merge the branch, then run the GitHub workflow that creates a GPG-signed tag. Pushing that tag triggers the publish pipeline.

GitHub Actions handles packaging, publishing, and creating the GitHub release once the tag is pushed.

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
6. Pre-populates `CHANGELOG.md` with the commits since the previous tag and lets you edit.
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

1. Imports the release GPG key (from repository secrets).
2. Creates a `vX.Y.Z` signed tag on the current `main`.
3. Pushes the tag to `origin`.

The pushed tag triggers the `Publish to PyPI` workflow (`.github/workflows/publish.yml`).

> Tip: the workflow aborts if the tag is already present locally or on the remote, preventing accidental overwrites.

## Tag Signing Secrets (One-Time)

1. Generate a dedicated signing key (rotate annually or as needed):
    ```bash
    gpg --quick-gen-key "Miniflux TUI Release <release@reuteras.net>" rsa4096 sign 1y
    gpg --armor --export-secret-keys "Miniflux TUI Release" > release-key.asc
    ```
2. Add the following repository secrets (ideally scoped to the `pypi` environment):
    - `GPG_PRIVATE_KEY`: contents of `release-key.asc`
    - `GPG_PASSPHRASE`: the key passphrase
    - Optional overrides: `GPG_SIGNING_NAME`, `GPG_SIGNING_EMAIL`
3. When rotating the key, update the secrets and delete the old key from GitHub.

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

- If the signed-tag workflow fails in GitHub Actions, press “Re-run all jobs” or:
  ```bash
  gh run rerun <run-id>
  ```
- To create a tag locally in an emergency, use the release key and a signed tag:
  ```bash
  git checkout main
  git pull --ff-only
  git tag -s vX.Y.Z -m "vX.Y.Z"
  git push origin vX.Y.Z
  ```
  (Avoid this path unless absolutely necessary—automation keeps the provenance consistent.)

The publish workflow can be re-run from the GitHub Actions UI if needed.
