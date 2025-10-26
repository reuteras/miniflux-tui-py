# Release Process

This document describes the automated release process for miniflux-tui-py using GitHub Actions and Release Drafter.

## Overview

The release process is fully automated:

1. **PR Labels** → Contributors label PRs with appropriate categories
2. **Release Drafter** → Automatically creates/updates draft releases with organized notes
3. **Version Tag** → When ready, push a git tag (e.g., `v0.4.0`)
4. **CI/CD Pipeline** → Automatically builds, tests, publishes to PyPI, and creates release

## Step-by-Step Release Process

### 1. Ensure All Changes Are Merged to Main

All features must be merged to `main` via pull requests before release:

```bash
git checkout main
git pull origin main
```

### 2. Label Your PRs

When creating or updating PRs, use appropriate labels for automatic changelog organization:

**Feature Categories:**
- `feature` - New major features
- `enhancement` - Improvements to existing features
- `search` - Search functionality changes
- `theme` - Theme/UI customization changes

**Quality/Testing:**
- `test` - Test additions/improvements
- `coverage` - Test coverage improvements
- `quality` - Code quality improvements

**Maintenance:**
- `bugfix` or `fix` - Bug fixes
- `documentation` - Documentation updates
- `refactor` - Code refactoring
- `dependencies` - Dependency updates
- `chore` - Maintenance tasks

**Special:**
- `breaking` - Breaking changes (triggers major version bump)
- `skip-changelog` - Exclude from changelog

### 3. Review the Draft Release

Release Drafter automatically creates a draft release as PRs are labeled and merged. To view it:

```bash
gh release list --draft
```

Or visit: [Releases](https://github.com/reuteras/miniflux-tui-py/releases)

The draft release shows:
- Organized changes by category
- PR titles and links
- Author information
- Automatic version suggestions

### 4. Update Version Number (Optional)

If Release Drafter's version number doesn't match your intended version:

```bash
# Edit pyproject.toml
nano pyproject.toml

# Update version = "x.y.z"
```

### 5. Update CHANGELOG.md (Optional)

For significant releases, you may want to manually enhance the CHANGELOG with additional context:

```bash
# Edit CHANGELOG.md
nano CHANGELOG.md

# Add section: ## [x.y.z] - YYYY-MM-DD
```

### 6. Create and Push the Version Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release vX.Y.Z"

# Push tag to trigger CI/CD pipeline
git push origin vX.Y.Z
```

The tag format must match: `v[0-9]+.[0-9]+.[0-9]+` (e.g., `v0.4.0`)

### 7. CI/CD Pipeline Executes Automatically

Once the tag is pushed, the following happens automatically:

#### Phase 1: Tests & Validation (publish.yml - build job)
- Checks out code
- Runs `ruff` linting
- Runs `pyright` type checking
- Runs full test suite with coverage
- Builds distribution packages (wheel + sdist)
- Uploads artifacts

#### Phase 2: Publish to PyPI (publish.yml - publish job)
- Downloads artifacts
- Publishes to PyPI using OIDC (secure, no tokens needed)
- Creates PyPI release page

#### Phase 3: Create GitHub Release (publish.yml - release job)
- Downloads artifacts
- Publishes the draft release created by Release Drafter
- Attaches wheel and source distribution files
- Makes release public with professional notes

### 8. Verify the Release

```bash
# Check PyPI
pip install --upgrade miniflux-tui-py

# Check GitHub release
gh release view vX.Y.Z

# Check release assets
gh release view vX.Y.Z --json assets
```

## Release Drafter Configuration

Release Drafter is configured in `.github/release-drafter.yml`:

### Automatic Version Incrementing

- **Major** bump: PRs with `breaking` label
- **Minor** bump: PRs with `feature` or `enhancement` labels
- **Patch** bump: PRs with `bugfix`, `fix`, or `hotfix` labels
- **Default**: patch (if no labels match)

### Release Notes Categories

Categories are automatically populated based on PR labels:

1. **🚀 Major Features** - `feature`, `enhancement`
2. **🔍 Search & Discovery** - `search`
3. **🎨 Theme & UI Customization** - `theme`, `ui`
4. **✅ Testing & Quality** - `test`, `testing`, `coverage`, `quality`
5. **🐛 Bug Fixes** - `bugfix`, `fix`, `hotfix`
6. **📚 Documentation** - `documentation`, `docs`
7. **♻️ Refactoring** - `refactor`
8. **⚙️ Dependencies** - `dependencies`, `deps`
9. **🔧 Chores** - `chore`, `maintenance`

### Release Note Template

The template includes:
- Release title and version
- Overview section
- Organized changes by category
- Compatibility information
- Installation instructions
- Contribution acknowledgments

## CI/CD Workflows

### release-drafter.yml

**Triggers:** On push to main, on PR events

**Actions:**
- Runs Release Drafter
- Creates/updates draft release
- Organizes PRs by labels
- Generates changelog automatically

### publish.yml

**Triggers:** On git tags matching `v[0-9]+.[0-9]+.[0-9]+`

**Jobs:**
1. **build**: Tests, lints, type-checks, builds packages
2. **publish**: Publishes to PyPI
3. **release**: Publishes GitHub release with artifacts

## Example: Creating a Release

### Scenario: Release v0.5.0

```bash
# Ensure main is up to date
git checkout main
git pull origin main

# Check draft release
gh release list --draft
# Review organized changes in the draft

# (Optional) Update version in pyproject.toml
# (Optional) Update CHANGELOG.md

# Create and push tag
git tag -a v0.5.0 -m "Release v0.5.0"
git push origin v0.5.0

# Monitor CI/CD
gh run watch

# Verify release
gh release view v0.5.0
pip install --upgrade miniflux-tui-py
```

That's it! The release is automatically created and published.

## Troubleshooting

### Draft Release Doesn't Show My PR

**Cause:** PR not labeled or workflow hasn't run yet

**Solution:**
1. Add appropriate label to PR
2. Wait for Release Drafter workflow to run
3. Manually trigger: `gh workflow run release-drafter.yml`

### Wrong Version Number in Draft

**Cause:** Label-based version calculation

**Solution:**
1. Review PR labels
2. Add `breaking` label for major bump
3. Add `feature` label for minor bump
4. Or manually edit version in pyproject.toml before tagging

### CI/CD Failed After Tag Push

**Cause:** Tests failed or linting error

**Solution:**
1. Check failed workflow: `gh run view <run-id>`
2. Fix the issue locally
3. Commit and push fix
4. Delete tag: `git tag -d v0.5.0 && git push origin :refs/tags/v0.5.0`
5. Create new tag: `git tag -a v0.5.0 -m "Release v0.5.0"` and push

### Release Not Published to PyPI

**Cause:** Build job failed

**Solution:**
1. Check build logs: `gh run view <run-id> --log`
2. Fix issues
3. Retry by recreating tag

## Best Practices

✅ **Do:**
- Label all PRs with appropriate category
- Review draft release before tagging
- Use semantic versioning (major.minor.patch)
- Test locally before pushing tag
- Verify PyPI and GitHub release after publishing

❌ **Don't:**
- Push tags directly without PR review
- Skip PR labels (makes changelog less organized)
- Create multiple tags for same version
- Manually publish to PyPI (use CI/CD)

## References

- [Release Drafter Documentation](https://github.com/release-drafter/release-drafter)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
