# Update Required Status Check: build → MegaLinter

## Current Situation

The `linter.yml` workflow has a job called `megalinter`, but the main branch protection requires a status check called "build". This causes the check to never run.

**Current state:**
- Job name in workflow: `megalinter`
- Required status check: `build`
- Display name: `MegaLinter`

**Result:** The check doesn't appear because GitHub looks for a job called "build" but the workflow has "megalinter"

## Solution: Update Branch Protection

You need to change the required status check from "build" to "MegaLinter" (the display name).

### Step-by-Step Instructions

#### Option 1: Via GitHub Web UI (Recommended)

1. **Go to branch protection settings:**
    ```
    https://github.com/reuteras/miniflux-tui-py/settings/branch_protection_rules
    ```

2. **Find the rule for `main` branch**
    - Click on the existing rule (should show `main` or a pattern matching it)

3. **Update required status checks:**
    - Scroll to "Require status checks to pass before merging"
    - In the "Status checks that are required" section:
      - **Remove**: `build` (uncheck or remove it)
      - **Add**: `MegaLinter` (type it in the search box and select it)

    Note: The check must have run at least once for it to appear in the dropdown. Since PR #242 is running, "MegaLinter" should be available.

4. **Save changes:**
    - Scroll to bottom
    - Click "Save changes"

#### Option 2: Create New Branch Protection Rule (If needed)

If you need to create a fresh rule:

1. Go to: `https://github.com/reuteras/miniflux-tui-py/settings/branches`

2. Click "Add branch protection rule"

3. Configure:
    - **Branch name pattern**: `main`

    - **Protect matching branches**:
      - ✅ Require a pull request before merging
        - Required approvals: 0 (or your preference)
        - ✅ Dismiss stale pull request approvals when new commits are pushed

      - ✅ Require status checks to pass before merging
        - ✅ Require branches to be up to date before merging
        - **Status checks that are required**:
          - Add: `MegaLinter` (search and select)
          - Do NOT add: `build`

      - ✅ Include administrators (optional, for consistency)
      - ✅ Restrict who can push to matching branches (optional)

4. Click "Create" or "Save changes"

### Verification

After updating, verify the change:

```bash
# Check current required checks
gh api repos/reuteras/miniflux-tui-py/branches/main/protection \
  --jq '.required_status_checks.contexts'

# Should show:
# ["MegaLinter"]
```

Or check via UI:
1. Go to PR #242
2. Scroll to bottom
3. You should see "MegaLinter" as a required check
4. It should show "Pending" or "Success" (not missing)

## Why This is Better

### Before (Incorrect):
```yaml
# Workflow defines:
jobs:
  megalinter:  # ← Job ID
    name: MegaLinter  # ← Display name

# But GitHub looks for:
# Required check: "build"  # ← Doesn't exist!
```

### After (Correct):
```yaml
# Workflow defines:
jobs:
  megalinter:  # ← Job ID
    name: MegaLinter  # ← Display name

# GitHub looks for:
# Required check: "MegaLinter"  # ← Matches display name! ✅
```

## Alternative: Keep job name as "build"

If you prefer, we could rename the job back to "build":

```yaml
jobs:
  build:  # ← Keep job ID as "build"
    name: MegaLinter  # ← Display name can still be "MegaLinter"
```

But this is less semantic. It's better to:
- Keep job ID descriptive (`megalinter`)
- Update the required check to match display name (`MegaLinter`)

## Technical Details

GitHub status checks can match either:
1. **Job ID** (`megalinter` in our case)
2. **Display name** (`MegaLinter` via `name:` field)

The current requirement is looking for "build" which matches neither.

By changing the requirement to "MegaLinter", it will match the display name.

## After Making the Change

Once you update the branch protection:

1. **PR #242 will update:**
    - The "build" check will disappear (or show as optional)
    - The "MegaLinter" check will appear as required
    - Status should show correctly

2. **Future PRs will:**
    - Require "MegaLinter" to pass
    - No longer look for "build"

3. **Other jobs remain unchanged:**
    - `bandit` job still runs independently
    - `gitleaks` job still runs independently
    - All other workflows unaffected

## Let Me Know

Once you've made the change via GitHub UI, let me know and I can verify it's working correctly!

Alternatively, if you want me to try the API approach with proper permissions, I can help with that too.

---

**Current Status:**
- Workflow updated: ✅ (job is `megalinter`)
- Branch protection: ⏳ (needs manual update to `MegaLinter`)
- PR #242: ⏳ (waiting for branch protection update)
