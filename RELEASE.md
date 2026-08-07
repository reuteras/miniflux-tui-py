# Release Guide

This guide documents the **fully automated** release process for miniflux-tui-py. The entire process is handled by GitHub Actions - no local tools or manual steps required!

## Quick Start (TL;DR)

1. Go to: <https://github.com/reuteras/miniflux-tui-py/actions/workflows/release.yml>
2. Click "Run workflow"
3. Enter version (e.g., `0.5.3`) or choose bump type
4. Click "Run workflow"
5. Done! ☕ (Wait ~10 minutes for full release)

## What Happens Automatically

When you trigger the release workflow, GitHub Actions will:

1. ✅ Create a release branch with version bump and changelog
2. ✅ Create a PR to main
3. ✅ Wait for all CI checks to pass
4. ✅ Auto-merge the PR
5. ✅ Create a signed git tag (using Sigstore Gitsign)
6. ✅ Trigger the publish workflow:

- Build Python packages (wheel + sdist)
- Publish to PyPI with attestations
- Build binaries for Linux, macOS, Windows
- Generate SBOMs (CycloneDX + SPDX)
- Sign all artifacts with cosign
- Generate SLSA provenance
- **Publish GitHub release** (not a draft!)
- Mark as "latest" release

**Total time**: ~10-15 minutes from trigger to published release on PyPI and GitHub.

## Detailed Process

### Step 1: Trigger the Release Workflow

Navigate to the Actions tab and run the "Create Release" workflow:

```bash
# Option 1: Via GitHub UI
# Go to: https://github.com/reuteras/miniflux-tui-py/actions/workflows/release.yml
# Click "Run workflow" → Enter version → Run

# Option 2: Via GitHub CLI
gh workflow run release.yml --ref main --field version=0.5.3

# Option 3: Auto-bump with type
gh workflow run release.yml --ref main --field bump_type=patch  # or minor, major
```

### Step 2: Monitor Progress

```bash
# Watch the workflow
gh run watch

# Or check status
gh run list --workflow=release.yml --limit 1
```

The workflow will automatically:

- Create release PR
- Wait for CI to pass
- Merge the PR
- Create signed tag
- Trigger publish workflow

### Step 3: Verify Release

```bash
# Check PyPI
curl -s https://pypi.org/pypi/miniflux-tui-py/json | jq -r '.info.version'

# Check GitHub release
gh release view v0.5.3

# Test installation
pip install miniflux-tui-py --upgrade
```

## Release Artifacts

Each release includes:

### Python Packages

- `miniflux-tui-py-X.Y.Z.tar.gz` - Source distribution
- `miniflux_tui_py-X.Y.Z-py3-none-any.whl` - Wheel

### Standalone Binaries

- `miniflux-tui-linux-x86_64.tar.gz`
- `miniflux-tui-macos.tar.gz`
- `miniflux-tui-windows.zip`

### Security Artifacts

- `*.sig` - Cosign signatures for all artifacts
- `*.sig.bundle` - Signature bundles with certificates
- `*.cdx.json` - CycloneDX SBOMs
- `*.spdx.json` - SPDX SBOMs
- `provenance.json` - SLSA provenance document
- GitHub attestations (build provenance)

### Signatures and Verification

All artifacts are signed using Sigstore cosign with keyless signing (OIDC):

```bash
# Verify a release artifact
cosign verify-blob \
  --bundle miniflux-tui-py-0.5.3.tar.gz.sig.bundle \
  --certificate-identity-regexp "https://github.com/reuteras/miniflux-tui-py" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  miniflux-tui-py-0.5.3.tar.gz

# Verify git tag
git verify-tag v0.5.3
```

## Monitoring & Troubleshooting

### Check Workflow Status

```bash
# List recent runs
gh run list --limit 5

# Watch a specific run
gh run watch <RUN-ID>

# View logs
gh run view <RUN-ID> --log
```

### Common Issues

#### Problem: CI checks fail on release PR

**Solution**: The workflow will stop and the PR won't be merged. Fix the issues, then manually merge the PR or re-run the workflow.

#### Problem: Workflow fails at tag creation

**Solution**: Check if the version already exists. Delete the tag if needed:

```bash
git tag -d vX.Y.Z
git push origin :vX.Y.Z
```

Then re-run the workflow.

#### Problem: Release published but not showing as "latest"

**Solution**: This shouldn't happen anymore (we removed `--draft`), but if it does:

```bash
gh release edit vX.Y.Z --latest
```

### Re-running Failed Workflows

If any job fails, you can re-run it:

```bash
# Re-run entire workflow
gh run rerun <RUN-ID>

# Or via GitHub UI
# Go to Actions → Click on failed run → Re-run all jobs
```

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backwards compatible
- **PATCH** (0.0.X): Bug fixes, backwards compatible

When using `bump_type`:

- `patch`: 0.5.2 → 0.5.3
- `minor`: 0.5.2 → 0.6.0
- `major`: 0.5.2 → 1.0.0

## Security & Signing

### Keyless Signing with Sigstore

The release process uses **Sigstore Gitsign** and **Cosign** for keyless cryptographic signing:

- ✅ **No long-lived secrets** - Uses short-lived OIDC tokens
- ✅ **Automatic transparency log** - All signatures logged publicly
- ✅ **Consistent security** - Same approach for tags and artifacts
- ✅ **Reduced attack surface** - No private keys to manage

### Prerequisites

All signing is automatic! No local setup needed. The workflows require:

1. `id-token: write` permission (already configured)
2. GitHub provides OIDC tokens automatically
3. Gitsign/Cosign use these tokens for signing

### Transparency Logs

All signatures are publicly logged:

- Git tags: [Sigstore Rekor](https://rekor.sigstore.dev/)
- Artifacts: [Sigstore Rekor](https://rekor.sigstore.dev/)
- Attestations: [GitHub](https://github.com/reuteras/miniflux-tui-py/attestations)

## Changelog Generation

Changelogs are automatically generated using [git-cliff](https://git-cliff.org/) based on conventional commits:

### Conventional Commit Format

```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `refactor`: Code refactoring
- `test`: Test changes
- `ci`: CI/CD changes

### Examples

```bash
git commit -m "feat: add dark mode support"
git commit -m "fix: resolve crash on startup"
git commit -m "docs: update installation instructions"
```

## PyPI Trusted Publisher (One-Time Setup)

The first release requires PyPI trusted publisher configuration:

1. Visit <https://pypi.org/account/publishing/>
2. Add a trusted publisher with:

- **Project:** `miniflux-tui-py`
- **Repository owner:** `reuteras`
- **Repository name:** `miniflux-tui-py`
- **Workflow filename:** `publish.yml`
- **Environment:** `pypi`

This is already configured for this project.

## Manual / Emergency Release

If the automated workflow is unavailable, you can trigger a publish by pushing a signed tag directly:

```bash
git checkout main
git pull --ff-only
git tag -s vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

This triggers the publish workflow but skips the automatic PR/changelog steps.

## Complete Release Checklist

For the paranoid (or those who like checklists):

- [ ] Go to Actions → Create Release workflow
- [ ] Enter version or choose bump type
- [ ] Click "Run workflow"
- [ ] Wait for workflow to complete (~10 min)
- [ ] Verify PyPI has new version
- [ ] Verify GitHub release exists and is published
- [ ] Test installation: `pip install miniflux-tui-py --upgrade`
- [ ] 🎉 Celebrate!

## Timeline

**Total release time: ~10-15 minutes**

1. **Prepare** (1-2 min): Create branch, update version, generate changelog
2. **CI** (3-5 min): Run tests, checks on PR
3. **Merge** (1 min): Auto-merge PR
4. **Publish** (5-7 min): Build, sign, publish to PyPI, create GitHub release

No manual intervention required at any step!
