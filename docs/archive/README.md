# Archived Documentation

This directory contains documentation that is no longer actively maintained but kept for historical reference.

## Files

### Release Process (Archived)
- **release.py** - Old Python release script (replaced by release.yml workflow)
- **release-process.md** - Old manual release documentation
- **RELEASE_TROUBLESHOOTING.md** - Troubleshooting for old release process
- **RELEASE_WORKFLOW_ANALYSIS.md** - Analysis of old workflow

**Replaced by**: `.github/workflows/release.yml` and updated `RELEASE.md`

### Coverage Analysis (Archived)
- **coverage_analysis.md** - Snapshot of test coverage from a specific point in time

**Note**: Run `uv run pytest --cov=miniflux_tui --cov-report=term-missing` for current coverage.

### Tool Documentation (Archived)
- **free-tool-alternatives.md** - Comparison of free development tools
- **quick-reference-free-tools.md** - Quick reference for free tools
- **RENOVATE_MIGRATION.md** - Migration guide from Dependabot to Renovate

**Note**: Project currently uses Renovate and uv for dependency management.

### Branch Protection (Archived)
- **UPDATE_BRANCH_PROTECTION.md** - Instructions for updating GitHub branch protection

**Note**: Branch protection is configured. Changes should be made through repository settings.

## Why Archived?

These documents were moved to the archive because:
1. They describe outdated processes or tools
2. They've been replaced by newer documentation
3. They're specific to a point in time and no longer reflect current state
4. They're kept for historical reference or audit purposes

## Current Documentation

For up-to-date documentation, see:
- [RELEASE.md](../../RELEASE.md) - Current release process
- [DEVELOPMENT.md](../../DEVELOPMENT.md) - Development setup
- [docs/](../) - Main documentation directory
