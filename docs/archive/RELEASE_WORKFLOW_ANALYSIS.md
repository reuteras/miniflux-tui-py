# Release Workflow Analysis

## Overview of the Release Process

### 1. **Create Signed Tag** (`create-signed-tag.yml`)

**Trigger:** Manual workflow dispatch
- Manually triggered via GitHub Actions UI
- Requires version input (e.g., "0.5.2")

**What it does:**
- Creates a signed git tag using Gitsign (keyless signing with OIDC)
- Tag format: `v{VERSION}` (e.g., v0.5.2)
- Pushes the signed tag to the repository

**Important:** This is the **first step** in the release process and must be done manually.

---

### 2. **Publish Workflow** (`publish.yml`)

**Trigger:** Push of a version tag
```yaml
on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"
```

**Triggered by:** The signed tag created in step 1

**What it does (in order):**

#### Build Job:
1. Runs tests and type checking
2. Builds Python distribution (wheel + sdist)
3. Uploads artifacts for later use

#### Publish Job:
1. Downloads build artifacts
2. Publishes to PyPI with attestations
3. Uses trusted publishing (OIDC)

#### Binaries Job:
1. Builds standalone executables for Linux, macOS, and Windows
2. Uploads binary artifacts

#### Release Job (THE KEY ONE):
1. Downloads all artifacts (dist, binaries)
2. **Generates SBOMs** using Syft (CycloneDX + SPDX formats)
3. **Generates GitHub attestations** for all artifacts
4. **Signs all artifacts** with cosign (keyless signing)
5. **Generates SLSA provenance** documents
6. **Creates draft release** with all assets:
   - Python packages (.whl, .tar.gz)
   - Binary executables
   - SBOMs (.cdx.json, .spdx.json)
   - Signatures (.sig, .sig.bundle)
   - Provenance (provenance.json)

**Key Code (Line 376):**
```yaml
gh release create "${TAG}" --draft --verify-tag --title "${TAG}" --notes "${RELEASE_NOTES}" --repo "${REPO}"
```

The release is created as a **draft** (`--draft` flag).

---

### 3. **Release Drafter** (`release-drafter.yml`)

**Trigger:** Push to main branch
```yaml
on:
  push:
    branches:
      - main
```

**What it does:**
- Maintains a draft release with automatically generated release notes
- Updates the draft as PRs are merged to main
- Does NOT publish the release

---

### 4. **Scorecard Analysis** (`scorecard.yml`)

**Triggers:**
```yaml
on:
  branch_protection_rule:
  push:
    branches: [main]
    paths: [code/config files]
  pull_request:
    branches: [main]
    paths: [code/config files]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
```

**When it runs:**
- On pushes to main (AFTER tag is pushed)
- On PRs to main
- Weekly on schedule
- When branch protection rules change

---

## Timeline and Order

### Actual Release Flow:

1. **Manual:** Run `create-signed-tag.yml` → Creates tag `v0.5.x`
2. **Automatic:** Tag push triggers `publish.yml` → Builds, signs, creates **draft release**
3. **Automatic:** Push to main triggers `scorecard.yml` → Runs analysis
4. **Manual:** Someone must manually publish the release from draft

### Answer to Your Questions:

#### Q: What triggers `create-signed-tag.yml`?
**A:** Manual workflow dispatch only (workflow_dispatch event)

#### Q: What makes the release "latest" and not a draft?
**A:** Two things are needed:
1. The release is initially created as a **draft** (line 376 in publish.yml)
2. Someone must **manually publish** it through the GitHub UI (Releases page)
3. GitHub automatically marks the most recent non-draft, non-prerelease as "latest"

#### Q: Does this happen before scorecard runs?
**A:** No, scorecard runs AFTER the tag is pushed to main:
- Tag push → `publish.yml` runs (creates draft release with SBOMs, signatures, etc.)
- Tag push to main → `scorecard.yml` runs
- So all the signed files, SBOMs, and artifacts ARE created before scorecard runs
- But scorecard also runs on PRs and weekly, not just releases

---

## Current Gap: Manual Release Publishing

The workflow creates a **draft release** with all the proper artifacts, but it requires manual intervention to:
1. Review the draft release
2. Click "Publish release" in GitHub UI
3. This makes it visible and marks it as "latest"

### Recommendation:

To automate the "publish" step, add this to the end of the `release` job in `publish.yml`:

```yaml
- name: Publish release
  if: github.run_attempt == 1
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    RELEASE_TAG: ${{ env.RELEASE_TAG }}
  run: |
    gh release edit "${RELEASE_TAG}" --draft=false --latest
```

This would automatically publish the release after all assets are uploaded.

---

## Summary

✅ **SBOMs, signatures, and attestations** ARE created before scorecard runs
✅ **Scorecard runs** on pushes to main (which includes tag pushes)
❌ **Release publishing** currently requires manual action
⚠️ **Gap:** Draft releases don't become "latest" automatically
