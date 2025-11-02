# Renovate Migration Guide: Mend.io → Self-Hosted

Complete step-by-step guide to migrate miniflux-tui-py from Mend.io hosted Renovate to your self-hosted Renovate instance.

**Date**: November 1, 2025
**Repository**: reuteras/miniflux-tui-py
**Current Setup**: Mend.io hosted Renovate
**Target Setup**: Self-hosted Renovate (same as your Forgejo setup)

---

## Prerequisites ✅

Before starting, ensure you have:
- [ ] Admin access to reuteras/miniflux-tui-py repository
- [ ] Self-hosted Renovate instance running (you mentioned you have this for Forgejo)
- [ ] GitHub Personal Access Token with `repo` scope (or GitHub App)
- [ ] Access to your self-hosted Renovate configuration

---

## Phase 1: Remove Mend.io Renovate Access

### Step 1.1: Check Current Installation

1. Go to your GitHub repository settings:
    ```
    https://github.com/reuteras/miniflux-tui-py/settings/installations
    ```

2. Look for these possible names:
    - "Renovate"
    - "Mend Renovate"
    - "WhiteSource Renovate"
    - "Renovate Bot"

### Step 1.2: Remove Repository Access

**Option A: If it's a repository-level installation:**

1. Click on the installation name
2. Click "Configure" button
3. Scroll to "Repository access"
4. Either:
    - Select "Only select repositories" and remove `miniflux-tui-py`
    - Or uninstall completely if this is the only repo using it
5. Click "Save"

**Option B: If it's an organization/user-level installation:**

1. Go to: `https://github.com/settings/installations`
2. Find "Renovate" or "Mend Renovate"
3. Click "Configure"
4. Under "Repository access", remove `reuteras/miniflux-tui-py`
5. Click "Save"

**Option C: Complete uninstall (if no other repos need it):**

1. Go to: `https://github.com/settings/installations`
2. Find "Renovate" or "Mend Renovate"
3. Click "Configure"
4. Scroll to bottom
5. Click "Uninstall"
6. Confirm the uninstallation

### Step 1.3: Verify Removal

After removal, verify:
```bash
# Check for new Renovate PRs - there should be none
gh pr list --author app/renovate --state open

# Should return empty or no recent PRs
```

---

## Phase 2: Verify .renovaterc.json Configuration

Your existing configuration is already excellent! Just verify it's correct.

### Step 2.1: Review Current Config

```bash
cd /path/to/miniflux-tui-py
cat .renovaterc.json
```

**Key settings to verify:**

```json
{
    "github-actions": {
        "enabled": true,
        "automerge": false,
        "pinDigests": true  // ← CRITICAL: This adds SHA hashes!
    }
}
```

### Step 2.2: Optional Improvements

Consider these additions (optional):

```json
{
    "$schema": "https://docs.renovatebot.com/renovate-schema.json",
    "extends": ["config:recommended"],
    "semanticCommits": "enabled",
    "commitMessagePrefix": "chore(deps):",
    "prCreation": "auto",
    "prConcurrentLimit": 2,

    "github-actions": {
        "enabled": true,
        "automerge": false,
        "pinDigests": true,
        "major": {
            "enabled": true
        }
    },

    "schedule": [
        "after 10pm on monday"
    ],

    "packageRules": [
        {
            "description": "Security patches: immediate updates",
            "matchUpdateTypes": ["patch"],
            "matchDatasources": ["github-actions"],
            "schedule": ["at any time"],
            "groupName": "github-actions-security",
            "automerge": false
        },
        {
            "description": "Major updates: weekly review",
            "matchUpdateTypes": ["major"],
            "matchDatasources": ["github-actions"],
            "automerge": false,
            "schedule": ["after 10pm on sunday"],
            "groupName": "github-actions-major"
        },
        {
            "description": "Disable Python package management",
            "matchCategories": ["python"],
            "enabled": false
        },
        {
            "description": "Pin SLSA version",
            "matchDatasources": ["github-tags"],
            "allowedVersions": "<=2.0.0",
            "matchPackageNames": ["/slsa-framework/slsa-github-generator/"]
        }
    ],

    "npm": {
        "enabled": false
    }
}
```

**No changes needed if current config looks good!**

---

## Phase 3: Configure Self-Hosted Renovate

### Step 3.1: Locate Your Renovate Configuration

Your self-hosted Renovate likely has a configuration file. Common locations:

**For Docker-based setup:**
```bash
# Usually in your Renovate config directory
~/renovate/config.js
~/renovate/renovate.json
~/renovate/repos.json
```

**For Kubernetes/other setups:**
- ConfigMap with Renovate settings
- Environment variables in deployment
- Separate config repository

### Step 3.2: Add Repository to Renovate Config

**Option A: Using config.js (JavaScript configuration):**

```javascript
module.exports = {
  platform: 'github',
  token: process.env.RENOVATE_TOKEN,

  // Add your repository here
  repositories: [
    'reuteras/miniflux-tui-py',
    // ... your other repositories
  ],

  // Optional: Global defaults (can be overridden by .renovaterc.json)
  gitAuthor: 'Renovate Bot <bot@renovateapp.com>',
  onboarding: false, // Disable onboarding since you already have .renovaterc.json
  requireConfig: 'required',

  // Your other configuration...
}
```

**Option B: Using repos.json (Simple list):**

```json
[
  "reuteras/miniflux-tui-py"
]
```

**Option C: Using environment variable:**

```bash
# Add to your Renovate startup script/environment
export RENOVATE_REPOSITORIES="reuteras/miniflux-tui-py"

# Or append to existing:
export RENOVATE_REPOSITORIES="existing-repo,reuteras/miniflux-tui-py"
```

### Step 3.3: Verify GitHub Token Access

Your Renovate needs a GitHub token with these permissions:

**Required Scopes:**
- ✅ `repo` (full repository access)
- ✅ `workflow` (to update GitHub Actions workflows)

**Verify token:**
```bash
# Test token access
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/reuteras/miniflux-tui-py

# Should return repository details
```

**If you need a new token:**
1. Go to: `https://github.com/settings/tokens`
2. Click "Generate new token (classic)"
3. Name: "Renovate Bot - miniflux-tui-py"
4. Select scopes:
    - [x] `repo` (all)
    - [x] `workflow`
5. Click "Generate token"
6. Copy token and store securely
7. Add to your Renovate configuration

---

## Phase 4: First Run and Testing

### Step 4.1: Manual Test Run

**If using Docker:**

```bash
# Dry-run first (no changes)
docker run --rm \
  -e RENOVATE_TOKEN=your_github_token \
  -e RENOVATE_REPOSITORIES=reuteras/miniflux-tui-py \
  -e LOG_LEVEL=debug \
  renovate/renovate:latest \
  --dry-run=full

# Check the logs for:
# - Repository discovered
# - Dependencies found
# - PRs that would be created
```

**If using other method:**
```bash
# Run your self-hosted Renovate with debug logging
renovate --dry-run=full reuteras/miniflux-tui-py
```

### Step 4.2: Review Dry-Run Output

Look for these in the logs:

```
✅ "Discovered 10+ dependencies"
✅ "github-actions manager found X dependencies"
✅ "pinDigests: Adding digests to GitHub Actions"
✅ "Would create PR: chore(deps): Update GitHub Actions"
```

### Step 4.3: Real Run (Create PRs)

Once dry-run looks good:

```bash
# Remove --dry-run flag
docker run --rm \
  -e RENOVATE_TOKEN=your_github_token \
  -e RENOVATE_REPOSITORIES=reuteras/miniflux-tui-py \
  renovate/renovate:latest
```

### Step 4.4: Verify First PR

Within minutes, you should see a PR like:

**Title**: `chore(deps): Update GitHub Actions`

**Content will include changes like:**
```yaml
# Before:
uses: actions/checkout@v5

# After:
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v5
```

**What to check:**
- ✅ PR created successfully
- ✅ SHA hashes added to all actions
- ✅ Comments show version tags (# v5)
- ✅ CI checks pass
- ✅ Commit signed by Renovate bot

---

## Phase 5: Ongoing Operations

### Step 5.1: Schedule Renovate Runs

**Using cron (recommended):**

```bash
# Add to crontab
# Run every Monday at 10 PM (matching your schedule in .renovaterc.json)
0 22 * * 1 /path/to/run-renovate.sh

# Example run-renovate.sh:
#!/bin/bash
docker run --rm \
  -e RENOVATE_TOKEN=${RENOVATE_TOKEN} \
  -e RENOVATE_REPOSITORIES=reuteras/miniflux-tui-py \
  renovate/renovate:latest
```

**Using systemd timer:**

```ini
# /etc/systemd/system/renovate.timer
[Unit]
Description=Renovate Bot Timer

[Timer]
OnCalendar=Mon *-*-* 22:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Step 5.2: Monitor Renovate Activity

**Check for PRs:**
```bash
gh pr list --author app/renovate
```

**Review Renovate logs:**
```bash
# Docker logs
docker logs renovate-container

# Or your logging system
```

**Verify schedule is working:**
```bash
# Check last run time
gh pr list --author app/renovate --json createdAt --limit 1
```

---

## Phase 6: Verify SHA Hash Updates

### Step 6.1: Check Our Current PRs

After Renovate runs, it should create a PR to update our three PRs:

**Expected changes to:**
- `.github/workflows/test.yml`
- `.github/workflows/semgrep.yml`
- `.github/workflows/linter.yml`

**Example change:**
```yaml
# Our current PR #240:
uses: py-cov-action/python-coverage-comment-action@v3

# Renovate will update to:
uses: py-cov-action/python-coverage-comment-action@a1b2c3d4e5f6... # v3
```

### Step 6.2: Merge Strategy

When Renovate PR arrives:

1. **Review the PR carefully**
    - Check all SHA hashes are valid
    - Verify version tags match (# v3, # v5, etc.)
    - Ensure CI passes

2. **Test locally (optional)**
    ```bash
    gh pr checkout <renovate-pr-number>
    # Verify YAML is valid
    yamllint .github/workflows/*.yml
    ```

3. **Merge the Renovate PR**
    ```bash
    gh pr merge <pr-number> --squash
    ```

4. **Our PRs will automatically update**
    - GitHub will show conflicts or need rebase
    - Either rebase or close/recreate with updated actions

---

## Troubleshooting

### Issue: Renovate Not Creating PRs

**Possible causes:**

1. **Token permissions insufficient**
    ```bash
    # Verify token scopes
    gh auth status
    ```

2. **Repository not in config**
    ```bash
    # Check Renovate config
    cat ~/renovate/config.js | grep miniflux-tui-py
    ```

3. **Renovate cache issue**
    ```bash
    # Clear Renovate cache
    docker run --rm \
      -e RENOVATE_TOKEN=token \
      -e RENOVATE_REPOSITORIES=reuteras/miniflux-tui-py \
      renovate/renovate:latest \
      --recreate-closed=true
    ```

### Issue: Wrong SHA Hashes

**Solution:**
```bash
# Force recreation of PRs
renovate --recreate-closed=true --rebase-stale-prs=true
```

### Issue: Too Many PRs Created

**Solution:** Adjust `.renovaterc.json`:
```json
{
    "prConcurrentLimit": 1,
    "prHourlyLimit": 2,
    "groupName": "all-updates",
    "groupSlug": "all"
}
```

---

## Verification Checklist

After completing all steps:

- [ ] Mend.io Renovate removed from GitHub settings
- [ ] No new PRs from `app/renovate` (Mend.io)
- [ ] Repository added to self-hosted Renovate config
- [ ] Self-hosted Renovate has valid GitHub token
- [ ] Dry-run completed successfully
- [ ] First PR created with SHA hashes
- [ ] CI passes on Renovate PR
- [ ] Schedule configured (cron/systemd)
- [ ] Monitoring set up
- [ ] Documentation updated

---

## Expected Timeline

- **Mend.io removal**: 5 minutes
- **Self-hosted config update**: 10 minutes
- **First dry-run**: 5 minutes
- **First real run & PR**: 10 minutes
- **Total**: ~30 minutes

---

## Next Steps After Migration

1. **Merge first Renovate PR** with SHA hashes
2. **Update our current PRs** (#240, #241, #242) or close and let Renovate recreate
3. **Monitor for 1 week** to ensure everything works
4. **Adjust schedule/config** as needed
5. **Document the new process** for team

---

## Support Resources

- **Renovate Docs**: https://docs.renovatebot.com/
- **Self-hosted guide**: https://docs.renovatebot.com/getting-started/running/#self-hosting-renovate
- **GitHub Platform**: https://docs.renovatebot.com/modules/platform/github/
- **Your setup**: Same as Forgejo setup (refer to your Forgejo Renovate config)

---

## Questions?

If you encounter issues:

1. Check Renovate logs (usually most helpful)
2. Verify GitHub token permissions
3. Test with dry-run first
4. Check `.renovaterc.json` is valid JSON
5. Ask me for help! I can debug specific errors

---

**Status**: Ready to execute
**Risk**: Low (non-destructive, can revert)
**Benefit**: Full control, SHA hashes, no rate limits

Would you like me to help with any specific step?
