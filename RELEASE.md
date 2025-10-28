# Release Guide

This guide explains how to create and publish new releases of miniflux-tui-py.

## Quick Start

The entire release process is automated with a simple command:

```bash
uv run python scripts/release.py
```

This Python script automates the entire release workflow and works across Windows, macOS, and Linux.

## What Gets Automated

The release script handles:

1. ✅ **Pre-Release Checks**
- Runs all tests (pytest with coverage)
- Checks code formatting (ruff)
- Validates type hints (pyright)

2. ✅ **Version Management**
- Prompts for new version number
- Validates semantic versioning format (e.g., 0.2.1)
- Updates `pyproject.toml`

3. ✅ **Documentation**
- Opens `CHANGELOG.md` for editing
- Verifies the changelog was updated

4. ✅ **Git Operations**
- Creates a commit with version bump and changelog
- Creates an annotated git tag
- Pushes everything to GitHub

5. ✅ **Automatic CI/CD**
- GitHub Actions workflow triggers automatically
- Runs full test suite
- Builds distribution packages
- Builds standalone binaries for Linux/macOS/Windows
- Publishes to PyPI
- Creates GitHub Release with artifacts

## Prerequisites

Before releasing, ensure:

- [ ] You're on the `main` branch
- [ ] All changes are committed (clean working directory)
- [ ] You have permissions to push to the repository
- [ ] PyPI is configured with Trusted Publisher (see below)

## Step-by-Step Guide

### 1. Start the Release

```bash
python scripts/release.py
```

You'll see:
```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
miniflux-tui-py Release Script
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[i] Current version: 0.2.0
Enter new version (e.g., 0.2.1):
```

### 2. Enter New Version

Type the new version using semantic versioning:
- `0.2.1` for patch release (bug fixes)
- `0.3.0` for minor release (new features)
- `1.0.0` for major release (breaking changes)

Example:
```text
New version: 0.2.1
✓ Version validated: 0.2.1
```

### 3. Wait for Pre-Release Checks

The script runs:
- Tests (215 tests)
- Linting (ruff)
- Type checking (pyright)

All must pass. If any fail, fix the issues and run the script again.

### 4. Edit Changelog

An editor will open with your `CHANGELOG.md` file.

Add a new section at the top (before the existing v0.2.0 section):

```markdown
## [0.2.1] - 2025-10-25

### Added
- New feature description

### Changed
- Improvement description

### Fixed
- Bug fix description
```

Save and close the editor (the script will verify the changelog was updated).

### 5. Release Created

The script will:
- ✓ Update `pyproject.toml` with new version
- ✓ Create a commit
- ✓ Create a git tag
- ✓ Push to GitHub

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Release Complete! 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version:      v0.2.1
Release Tag:  v0.2.1
GitHub:       https://github.com/reuteras/miniflux-tui-py/releases/tag/v0.2.1
PyPI:         https://pypi.org/project/miniflux-tui-py/0.2.1/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6. GitHub Actions Automation

Once you push the tag, GitHub Actions automatically:

1. **Build Job** (in parallel)
- Checks out code
- Runs ruff linting
- Runs pyright type checking
- Runs pytest (215 tests)
- Builds distribution packages (tar.gz + wheel)

2. **Publish Job** (after build succeeds)
- Downloads artifacts
- Publishes to PyPI using Trusted Publisher
- No secrets required!

3. **Binary Job** (after build succeeds)
- Runs on Linux, macOS, and Windows runners
- Builds PyInstaller-based standalone executables
- Packages OS-specific archives and uploads them as artifacts

4. **Release Job** (after build and binary jobs succeed)
- Creates GitHub Release
- Attaches distribution and binary artifacts
- Auto-generates release notes

5. **Container Image Job** (triggered on `main` and tags)
- Builds a multi-architecture image (linux/amd64 + linux/arm64)
- Pushes to GitHub Container Registry with branch, semver, and `latest` tags
- Generates SBOM and SLSA provenance attestations
- Signs the image with Sigstore Cosign (keyless via GitHub OIDC)

### 7. Verify Release

Monitor the workflow:
```text
https://github.com/reuteras/miniflux-tui-py/actions
```

Check PyPI (usually within 1-2 minutes):
```text
https://pypi.org/project/miniflux-tui-py/
```

Users can now install the new version:
```bash
pip install miniflux-tui-py==0.2.1
uv add miniflux-tui-py==0.2.1
```

## PyPI Trusted Publisher Setup (One-Time Only)

For automatic PyPI publishing without storing secrets:

1. Go to [https://pypi.org/account/publishing/](https://pypi.org/account/publishing/)
2. Click "Add a new trusted publisher"
3. Fill in:
- **PyPI Project Name:** `miniflux-tui-py`
- **GitHub Repository Owner:** `reuteras`
- **GitHub Repository Name:** `miniflux-tui-py`
- **Workflow Filename:** `publish.yml`
- **Environment Name:** `pypi`
4. Click "Add trusted publisher"

That's it! No API tokens needed.

## Troubleshooting

### Tests Failed

```text
✗ Tests failed. Fix issues before releasing.
```

**Fix:**
```bash
uv run pytest tests --cov=miniflux_tui
# See what failed and fix it
```

### Linting Failed

```text
✗ Linting failed. Run 'uv run ruff check miniflux_tui tests' to see issues.
```

**Fix:**
```bash
uv run ruff check miniflux_tui tests
uv run ruff format miniflux_tui tests  # Auto-format
```

### Type Checking Failed

```text
✗ Type checking failed. Run 'uv run pyright miniflux_tui tests' to see issues.
```

**Fix:**
```bash
uv run pyright miniflux_tui tests
# Fix type errors in the code
```

### Working Directory Not Clean

```text
✗ Working directory is not clean. Please commit or stash changes first.
```

**Fix:**
```bash
git status
git add .
git commit -m "Your message"
# Then run release script again
```

### CHANGELOG Not Updated

```text
✗ CHANGELOG.md was not updated
```

**Fix:**
The script will revert the version change. Edit `CHANGELOG.md` manually, then run the script again.

### GitHub Actions Failed

Check the workflow logs at:
```text
https://github.com/reuteras/miniflux-tui-py/actions
```

Common issues:
- **PyPI trusted publisher not configured** - See "PyPI Trusted Publisher Setup" above
- **Tests failing in CI** - These would have failed locally too
- **Secrets misconfigured** - We don't use secrets, only Trusted Publisher

## Version Numbering

Use **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **PATCH** (0.2.1): Bug fixes, no new features
```bash
# Example: 0.2.0 → 0.2.1
```

- **MINOR** (0.3.0): New features, backward compatible
```bash
# Example: 0.2.0 → 0.3.0
```

- **MAJOR** (1.0.0): Breaking changes
```bash
# Example: 0.2.0 → 1.0.0
```

## Release Checklist

Before running the release script:

- [ ] All work is committed
- [ ] You're on the `main` branch
- [ ] Branch is up-to-date: `git pull origin main`
- [ ] You know the new version number
- [ ] CHANGELOG notes are ready

After the release:

- [ ] Check GitHub Actions workflow passed
- [ ] Verify release on GitHub: [https://github.com/reuteras/miniflux-tui-py/releases](https://github.com/reuteras/miniflux-tui-py/releases)
- [ ] Verify on PyPI: [https://pypi.org/project/miniflux-tui-py/](https://pypi.org/project/miniflux-tui-py/)
- [ ] Pull the container image from GHCR and verify signature: `docker pull ghcr.io/reuteras/miniflux-tui:latest && cosign verify ghcr.io/reuteras/miniflux-tui:latest`
- [ ] Test installation: `pip install miniflux-tui-py --upgrade`

## Manual Release (Advanced)

If the script fails for any reason, you can do it manually:

```bash
# 1. Update version
sed -i 's/version = "0.2.0"/version = "0.2.1"/' pyproject.toml

# 2. Edit CHANGELOG.md manually

# 3. Commit
git add pyproject.toml CHANGELOG.md
git commit -m "chore: Release v0.2.1"

# 4. Create tag
git tag -a v0.2.1 -m "Release v0.2.1"

# 5. Push (this triggers CI/CD)
git push origin main v0.2.1
```

## Questions?

See:
- [CHANGELOG.md](CHANGELOG.md) - Release history
- [README.md](README.md) - User guide
- [Contributing Guide](docs/contributing.md) - Development guide
- [GitHub Issues](https://github.com/reuteras/miniflux-tui-py/issues) - Report problems

---

**Happy releasing!** 🚀
