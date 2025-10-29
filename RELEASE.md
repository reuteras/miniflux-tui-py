# Release Guide

Releases are now driven entirely from Git tags. The process happens in two stages:

1. Prepare a release branch that updates the version and changelog.
2. Merge the branch, tag `main`, and push the tag to trigger the publish workflow.

GitHub Actions handles packaging, publishing, and creating the GitHub release once the tag is pushed.

## Quick Start

```bash
# 1. Prepare the release branch with version + changelog updates
uv run python scripts/release.py

# 2. After the PR merges, tag the merged commit on main
uv run python scripts/release.py tag
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

> Tip: The script prints the exact `uv run python scripts/release.py tag --version X.Y.Z` command to run once the PR merges.

## Stage 2 - Create and Push the Tag

After the release branch merges:

```bash
git checkout main
git pull --ff-only
uv run python scripts/release.py tag
```

The `tag` sub-command:

1. Confirms `main` is clean and matches `origin/main`.
2. Reads the version from `pyproject.toml` (or use `--version` to override).
3. Creates an annotated tag `vX.Y.Z`.
4. Pushes the tag to GitHub.

Pushing the tag triggers the `Publish to PyPI` workflow (`.github/workflows/publish.yml`).

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

If the tag push fails (network issues, etc.), rerun:

```bash
git tag -d vX.Y.Z          # only if the tag was created locally
git pull --ff-only
uv run python scripts/release.py tag --version X.Y.Z
```

Or push manually:

```bash
git push origin vX.Y.Z
```

The CI workflow can be re-run from the GitHub Actions UI if needed.
