# Scripts Directory

This directory contains utility scripts for project maintenance and automation.

## Scripts Overview

### `approve_pr.sh`

Multi-account PR approval and release monitoring script that automates the PR workflow.

**Purpose:**
- Automates the approval process for PRs that require multiple reviewers
- Handles the complete workflow from draft to release
- Ensures OpenSSF Scorecard compliance (2+ reviewer requirement)

**Features:**
- Converts draft PRs to ready for review
- Approves PR from multiple GitHub accounts sequentially
- Waits for CI checks to pass
- Monitors PR merge status
- Optionally waits for release workflow completion
- Colored output with progress indicators
- Comprehensive error handling and timeout protection

**Prerequisites:**
1. GitHub CLI (`gh`) installed and authenticated
2. Multiple GitHub accounts configured with `gh auth login`:
  - `reuteras` (primary maintainer account)
  - `reuteras-review` (review account)
  - `reuteras-renovate` (automation account)
3. Accounts must have write access to the repository
4. Accounts must be configured in `.github/CODEOWNERS` if code owner review is required

**Setup:**

```bash
# Install GitHub CLI
brew install gh  # macOS
# or: sudo apt install gh  # Ubuntu/Debian
# or: choco install gh  # Windows

# Login to all accounts
gh auth login --hostname github.com  # Login as reuteras
gh auth login --hostname github.com  # Login as reuteras-review
gh auth login --hostname github.com  # Login as reuteras-renovate

# Verify accounts are logged in
gh auth status
```

**Usage:**

```bash
# Basic usage - approve PR and wait for release
./scripts/approve_pr.sh 123

# Approve PR but skip release monitoring
./scripts/approve_pr.sh 123 --skip-release-wait

# Make script executable (if needed)
chmod +x scripts/approve_pr.sh
```

**Workflow Steps:**

1. **Validation**: Checks if PR exists and is accessible
2. **Convert to Ready**: Marks draft PR as ready for review (if needed)
3. **Multi-Account Approval**: Switches between accounts and approves:
  - Switches to `reuteras` → approves
  - Switches to `reuteras-review` → approves
  - Switches to `reuteras-renovate` → approves
  - Skips accounts that are already approved or unavailable
4. **CI Monitoring**: Waits for all status checks to pass (max 30 min)
5. **Merge Monitoring**: Waits for PR to be auto-merged (max 10 min)
6. **Release Monitoring**: Waits for release workflow to complete (max 30 min, optional)

**Timeouts:**

- CI checks: 30 minutes
- PR merge: 10 minutes
- Release workflow: 30 minutes

**Exit Codes:**

- `0`: Success - all steps completed
- `1`: Failure - one or more steps failed or timed out

**Example Output:**

```text
ℹ ==========================================
ℹ PR Approval & Release Monitoring Script
ℹ ==========================================

ℹ Processing PR #123 in reuteras/miniflux-tui-py

ℹ Step 1: Converting draft to ready (if needed)
✅ PR #123 is now ready for review

ℹ Step 2: Approving from multiple accounts
ℹ Switching to account: reuteras
✅ Switched to reuteras
ℹ Approving PR #123 as reuteras...
✅ PR #123 approved by reuteras

ℹ Switching to account: reuteras-review
✅ Switched to reuteras-review
ℹ Approving PR #123 as reuteras-review...
✅ PR #123 approved by reuteras-review

✅ Approved by 2 account(s)

ℹ Step 3: Waiting for CI checks to pass
✅ All CI checks passed

ℹ Step 4: Waiting for PR to be merged
✅ PR #123 has been merged

ℹ Step 5: Waiting for release workflow
✅ Release workflow completed successfully

✅ ==========================================
✅ PR #123: All steps completed!
✅ ==========================================
```

**Troubleshooting:**

| Issue                               | Solution                                                |
|-------------------------------------|---------------------------------------------------------|
| "Failed to switch to account"       | Run `gh auth login` for the missing account             |
| "Failed to approve PR"              | Check account has write permissions to repo             |
| "Timeout waiting for CI checks"     | Check GitHub Actions for failing tests                  |
| "PR was not auto-merged"            | Verify branch protection rules allow auto-merge         |
| "Release workflow did not complete" | Check if version tag was created and workflow triggered |

**Notes:**

- The script preserves your original authenticated account after completion
- It skips accounts that have already approved the PR
- It requires all configured accounts to have appropriate permissions
- Use `--skip-release-wait` if you're not expecting a release or want faster completion

---

### `update_branch_protection.sh`

Updates GitHub branch protection rules for the `main` branch to comply with OpenSSF Scorecard requirements.

**Purpose:**
- Configures branch protection for security and code quality
- Ensures OpenSSF Scorecard compliance
- Prevents direct pushes to main branch

**Usage:**

```bash
./scripts/update_branch_protection.sh
```

**Protection Rules Applied:**
- Required approving reviews: 1+
- Dismiss stale reviews on new commits
- Last push approval required
- Linear history enforced
- Signed commits required
- Admin enforcement enabled
- Force pushes and deletions blocked

---

### `add_spdx_headers.py`

Adds SPDX license headers to Python source files for license compliance.

**Purpose:**
- Ensures all Python files have proper SPDX license identifiers
- Supports REUSE compliance for license management

**Usage:**

```bash
uv run scripts/add_spdx_headers.py
```

---

### `build_binary.py`

Builds standalone binary distributions of miniflux-tui using PyInstaller.

**Purpose:**
- Creates single-file executable for distribution
- Useful for users without Python installed

**Usage:**

```bash
uv run scripts/build_binary.py
```

## Best Practices

1. **Always test scripts in a fork first** before running on main repository
2. **Review script output** for errors or unexpected behavior
3. **Keep accounts secured** with 2FA and strong passwords
4. **Update scripts** when GitHub API or workflow changes occur
5. **Document changes** to scripts in commit messages

## Contributing

When adding new scripts:

1. Follow bash best practices:
  - Use `set -euo pipefail` for error handling
  - Add clear comments and documentation
  - Include usage examples
  - Add colored output for better UX
2. Make scripts executable: `chmod +x scripts/your_script.sh`
3. Update this README with script description and usage
4. Test thoroughly before committing

## Security

- Scripts use GitHub CLI authentication (no hardcoded tokens)
- Account switching uses `gh auth switch` (secure method)
- Scripts include timeout protection against infinite loops
- All API calls go through authenticated `gh` CLI

## Related Documentation

- [RELEASE.md](../RELEASE.md) - Release process documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [AGENT.md](../AGENT.md) - Project architecture and workflows
