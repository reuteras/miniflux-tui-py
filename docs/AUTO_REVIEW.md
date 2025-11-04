# Automated Review System

This document describes the automated review system using the `reuteras-review` bot account.

## Overview

Since this is a solo developer project, an automated review bot (`reuteras-review`) provides approvals for PRs after all automated checks pass. This satisfies GitHub's requirement for reviews while maintaining full automation.

## Configuration

### Bot Account
- **Username**: `reuteras-review`
- **Type**: User (with PAT token)
- **Purpose**: Automated PR reviews and approvals
- **Token**: Stored as `BOT_TOKEN` secret (expires 2025-10-31)

### Workflows

#### 1. Auto-Approve Passing PRs (`.github/workflows/auto-approve.yml`)

**Triggers:**
- `pull_request` events (opened, synchronize)
- `check_suite` events (completed) - currently skipped

**Behavior:**
1. Checks if PR is already approved
2. Waits for all status checks to complete
3. Verifies all checks passed
4. Approves PR using `BOT_TOKEN`

**Approved PR Sources:**
- `reuteras` (User) - Main developer
- `renovate[bot]` (Bot) - Dependency updates
- `dependabot[bot]` (Bot) - Security updates
- `github-actions[bot]` (Bot) - Automated workflows

**Conditions:**
- ✅ PR must not be a draft
- ✅ All status checks must pass
- ✅ No existing approval from bot
- ❌ Does NOT run on `check_suite` events (by if condition)

#### 2. Add Bot Reviews to Closed PRs (`.github/workflows/add-bot-reviews-to-closed-prs.yml`)

**Triggers:**
- `pull_request.closed` (when PRs are merged)
- `workflow_dispatch` (manual trigger)

**Purpose:** Retroactively adds bot reviews to merged PRs that didn't get one during the merge process.

**Review Message:**
```
✅ Automated review: All checks passed and requirements met.

This PR has been reviewed by automated checks:
- ✅ Code Quality (ruff, pyright)
- ✅ Security (CodeQL, Bandit, Gitleaks)
- ✅ Testing (pytest on Python 3.11-3.14)
- ✅ Workflow Analysis (malcontent, zizmor)
- ✅ Container Security (trivy, cosign)

Approved for merge.
```

## Current Status

### Branch Protection
```
Required approving reviews: 1 (ENFORCED via reuteras-review bot)
Dismiss stale reviews: true
Require last push approval: true
```

**Critical**: Reviews ARE now *required* by branch protection. The auto-approve workflow ensures PRs get the necessary approval automatically after all checks pass.

### Recent Activity
PR #431 was successfully auto-approved by `reuteras-review` after all checks passed.

## Workflow Issues & Fixes Needed

### Issue 1: check_suite Trigger Not Working

**Problem**: The workflow has a condition that skips ALL `check_suite` events:

```yaml
if: >-
  github.event_name == 'pull_request' &&
  github.event.pull_request.draft == false &&
  ...
```

This means approval only happens on:
- PR opened
- PR synchronized (new commits)

But NOT when checks complete.

**Impact**: If checks take time to complete, the PR might not get approved until the next push.

**Fix Options:**

1. **Option A**: Remove check_suite trigger (simplest)
  - Only approve on `pull_request` events
  - Approval happens when PR is updated, not when checks complete

2. **Option B**: Add separate job for check_suite events
  ```yaml
  auto-approve-on-checks:
    if: >-
      github.event_name == 'check_suite' &&
      github.event.check_suite.conclusion == 'success'
  ```

**Recommendation**: Option A - Remove check_suite trigger since it's not actually being used.

### Issue 2: No Commit Signing

**Current State**: The bot approves PRs but doesn't sign commits.

**Why This Matters:**
- Branch protection requires signed commits
- Bot reviews are signed (by nature of GitHub API)
- But the *approval* is not a commit signature

**Is This an Issue?**:
- ❌ **Not an issue** - The approval is separate from commit signing
- ✅ Commits are signed by the original author (reuteras)
- ✅ The bot's approval is tracked in GitHub's review system
- ✅ Branch protection checks commit signatures, not review signatures

## Verification

### Check if BOT_TOKEN is configured:
```bash
gh secret list | grep BOT_TOKEN
```

### Check recent auto-approvals:
```bash
gh run list --workflow=auto-approve.yml --limit 5
```

### Check PR reviews:
```bash
gh pr view <PR_NUMBER> --json reviews --jq '.reviews[] | {author: .author.login, state: .state}'
```

### Verify bot account:
```bash
gh api /users/reuteras-review --jq '{login, type, name}'
```

## Maintenance

### Token Expiration
- **Current Expiration**: 2025-10-31
- **Action Needed**: Regenerate token before expiration
- **Steps**:
  1. Go to https://github.com/settings/tokens (logged in as reuteras-review)
  2. Generate new classic PAT with `repo` scope
  3. Update `BOT_TOKEN` secret in repository settings

### Recommended Changes

1. **Remove check_suite trigger** (not functional):
  ```yaml
  on:
    pull_request:
      types: [opened, synchronize]
  ```

2. **Add workflow status to branch protection** (optional):
  - Currently: MegaLinter, Check Issue Link
  - Consider: Add "Auto-Approve PR" to required checks

3. **Simplify approval logic** (optional):
  - Current: Complex check for existing approvals
  - Could use: `actions/github-script` for simpler logic

## Security Considerations

### BOT_TOKEN Scope
- ✅ Limited to `repo` scope
- ✅ Stored as encrypted secret
- ✅ Only used in hardened workflows
- ✅ Audit logging enabled

### Approval Logic
- ✅ Only approves after ALL checks pass
- ✅ Only approves authorized PR authors
- ✅ Skip drafts
- ✅ Check existing approvals first

### Best Practices Followed
- ✅ Uses step-security/harden-runner
- ✅ Explicitly checks PR status
- ✅ Uses parameterized inputs (no template injection)
- ✅ Fails gracefully on errors

## Troubleshooting

### PR not getting auto-approved

1. **Check workflow run**:
  ```bash
  gh run list --workflow=auto-approve.yml --limit 1
  ```

2. **Check if workflow ran for the PR**:
  ```bash
  gh pr checks <PR_NUMBER>
  ```

3. **Verify PR author is in allow list**:
  - Must be: reuteras, renovate[bot], dependabot[bot], or github-actions[bot]

4. **Check if all status checks passed**:
  ```bash
  gh pr view <PR_NUMBER> --json statusCheckRollup
  ```

### Bot approval not showing

1. **Check BOT_TOKEN is valid**:
  ```bash
  # Try making a request with the token
  gh api /user -H "Authorization: token $BOT_TOKEN"
  ```

2. **Check workflow logs**:
  ```bash
  gh run view <RUN_ID> --log
  ```

## Summary

✅ **Working**: Bot account exists, token configured, workflow runs on PR events
✅ **Working**: Auto-approval happens after checks pass
✅ **Working**: Reviews are tracked in GitHub
⚠️ **Not Used**: check_suite trigger (blocked by if condition)
✅ **Not Needed**: Commit signing (handled separately by original author)

**Overall Status**: System is functional but could be optimized by removing unused check_suite trigger.
