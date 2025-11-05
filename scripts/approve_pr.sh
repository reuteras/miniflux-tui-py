#!/bin/bash
# Multi-account PR approval and release monitoring script
# This script automates the PR approval workflow by:
# - Converting draft PR to ready for review
# - Approving from multiple GitHub accounts (for 2+ reviewer requirement)
# - Waiting for CI checks to pass
# - Waiting for PR to be auto-merged
# - Monitoring release workflow completion
#
# Usage: ./scripts/approve_pr.sh PR_NUMBER [--skip-release-wait]

set -euo pipefail

# Configuration
REPO="reuteras/miniflux-tui-py"
ACCOUNTS=("reuteras" "reuteras-review" "reuteras-renovate")
CURRENT_ACCOUNT=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# Function to get current authenticated user
get_current_user() {
    gh api user --jq '.login' 2>/dev/null || echo ""
}

# Function to switch GitHub account
switch_account() {
    local account=$1
    log_info "Switching to account: $account"

    # Check if account is already logged in
    if gh auth status --hostname github.com 2>&1 | grep -q "$account"; then
        log_success "Already authenticated as $account"
        CURRENT_ACCOUNT=$account
        return 0
    fi

    # Try to switch account
    if gh auth switch --user "$account" 2>/dev/null; then
        log_success "Switched to $account"
        CURRENT_ACCOUNT=$account
        return 0
    else
        log_error "Failed to switch to $account. Please ensure account is logged in:"
        echo "  gh auth login --hostname github.com"
        return 1
    fi
}

# Function to check if PR exists
check_pr_exists() {
    local pr_number=$1
    if ! gh pr view "$pr_number" --repo "$REPO" &>/dev/null; then
        log_error "PR #$pr_number does not exist in $REPO"
        return 1
    fi
    return 0
}

# Function to convert draft to ready
convert_to_ready() {
    local pr_number=$1
    local is_draft

    is_draft=$(gh pr view "$pr_number" --repo "$REPO" --json isDraft --jq '.isDraft')

    if [ "$is_draft" = "true" ]; then
        log_info "PR #$pr_number is currently a draft. Converting to ready for review..."
        if gh pr ready "$pr_number" --repo "$REPO"; then
            log_success "PR #$pr_number is now ready for review"
        else
            log_error "Failed to convert PR to ready"
            return 1
        fi
    else
        log_info "PR #$pr_number is already ready for review"
    fi
    return 0
}

# Function to approve PR from current account
approve_pr() {
    local pr_number=$1
    local current_user

    current_user=$(get_current_user)
    log_info "Approving PR #$pr_number as $current_user..."

    # Check if already approved
    local reviews
    reviews=$(gh pr view "$pr_number" --repo "$REPO" --json reviews --jq ".reviews[] | select(.author.login == \"$current_user\" and .state == \"APPROVED\") | .state")

    if [ "$reviews" = "APPROVED" ]; then
        log_warning "Already approved by $current_user"
        return 0
    fi

    # Submit approval
    if gh pr review "$pr_number" --repo "$REPO" --approve --body "Approved via automated script"; then
        log_success "PR #$pr_number approved by $current_user"
    else
        log_error "Failed to approve PR #$pr_number as $current_user"
        return 1
    fi

    return 0
}

# Function to wait for CI checks to pass
wait_for_checks() {
    local pr_number=$1
    local max_wait=1800 # 30 minutes
    local elapsed=0
    local interval=30

    log_info "Waiting for CI checks to pass (max ${max_wait}s)..."

    while [ $elapsed -lt $max_wait ]; do
        local status
        status=$(gh pr view "$pr_number" --repo "$REPO" --json statusCheckRollup --jq '.statusCheckRollup[] | select(.conclusion != null) | .conclusion' | sort -u)

        # Check if all checks are successful
        if echo "$status" | grep -qvE '^(SUCCESS|SKIPPED|NEUTRAL)$'; then
            log_warning "Some checks are still pending or failed. Waiting ${interval}s..."
            sleep "$interval"
            elapsed=$((elapsed + interval))
            continue
        fi

        # Check if there are any pending checks
        local pending
        pending=$(gh pr view "$pr_number" --repo "$REPO" --json statusCheckRollup --jq '.statusCheckRollup[] | select(.conclusion == null) | .name')

        if [ -n "$pending" ]; then
            log_warning "Checks still running: $(echo "$pending" | tr '\n' ',' | sed 's/,$//')"
            sleep "$interval"
            elapsed=$((elapsed + interval))
            continue
        fi

        log_success "All CI checks passed"
        return 0
    done

    log_error "Timeout waiting for CI checks"
    return 1
}

# Function to wait for PR to be merged
wait_for_merge() {
    local pr_number=$1
    local max_wait=600 # 10 minutes
    local elapsed=0
    local interval=10

    log_info "Waiting for PR #$pr_number to be merged (max ${max_wait}s)..."

    while [ $elapsed -lt $max_wait ]; do
        local state
        state=$(gh pr view "$pr_number" --repo "$REPO" --json state --jq '.state')

        if [ "$state" = "MERGED" ]; then
            log_success "PR #$pr_number has been merged"
            return 0
        fi

        log_info "PR state: $state. Waiting ${interval}s..."
        sleep "$interval"
        elapsed=$((elapsed + interval))
    done

    log_error "Timeout waiting for PR to be merged"
    return 1
}

# Function to wait for release workflow
wait_for_release() {
    local pr_number=$1
    local max_wait=1800 # 30 minutes
    local elapsed=0
    local interval=30

    log_info "Waiting for release workflow to complete (max ${max_wait}s)..."

    # Get the merge commit SHA
    local merge_sha
    merge_sha=$(gh pr view "$pr_number" --repo "$REPO" --json mergeCommit --jq '.mergeCommit.oid')

    if [ -z "$merge_sha" ] || [ "$merge_sha" = "null" ]; then
        log_warning "Could not find merge commit SHA. Checking recent workflow runs..."
    fi

    while [ $elapsed -lt $max_wait ]; do
        # Check for recent release or publish workflows
        local workflow_status
        workflow_status=$(gh run list --repo "$REPO" --workflow=publish.yml --limit 1 --json status,conclusion,createdAt --jq '.[0] | "\(.status)|\(.conclusion)"')

        if [ -z "$workflow_status" ]; then
            # Try release workflow if publish not found
            workflow_status=$(gh run list --repo "$REPO" --workflow=release.yml --limit 1 --json status,conclusion,createdAt --jq '.[0] | "\(.status)|\(.conclusion)"')
        fi

        if [ -z "$workflow_status" ]; then
            log_info "No release workflow found yet. Waiting ${interval}s..."
            sleep "$interval"
            elapsed=$((elapsed + interval))
            continue
        fi

        IFS='|' read -r status conclusion <<<"$workflow_status"

        if [ "$status" = "completed" ]; then
            if [ "$conclusion" = "success" ]; then
                log_success "Release workflow completed successfully"
                return 0
            else
                log_error "Release workflow failed with conclusion: $conclusion"
                return 1
            fi
        fi

        log_info "Release workflow status: $status. Waiting ${interval}s..."
        sleep "$interval"
        elapsed=$((elapsed + interval))
    done

    log_error "Timeout waiting for release workflow"
    return 1
}

# Main function
main() {
    local pr_number=$1
    local skip_release_wait=${2:-""}

    echo ""
    log_info "=========================================="
    log_info "PR Approval & Release Monitoring Script"
    log_info "=========================================="
    echo ""

    # Validate PR number
    if ! [[ "$pr_number" =~ ^[0-9]+$ ]]; then
        log_error "Invalid PR number: $pr_number"
        echo "Usage: $0 PR_NUMBER [--skip-release-wait]"
        exit 1
    fi

    # Check if PR exists
    if ! check_pr_exists "$pr_number"; then
        exit 1
    fi

    log_info "Processing PR #$pr_number in $REPO"
    echo ""

    # Step 1: Convert to ready if draft
    log_info "Step 1: Converting draft to ready (if needed)"
    if ! convert_to_ready "$pr_number"; then
        exit 1
    fi
    echo ""

    # Step 2: Approve from multiple accounts
    log_info "Step 2: Approving from multiple accounts"
    local approval_count=0
    local original_account
    original_account=$(get_current_user)

    for account in "${ACCOUNTS[@]}"; do
        if switch_account "$account"; then
            if approve_pr "$pr_number"; then
                approval_count=$((approval_count + 1))
            fi
        else
            log_warning "Skipping $account due to authentication issues"
        fi
        echo ""
    done

    # Switch back to original account
    if [ -n "$original_account" ] && [ "$original_account" != "$CURRENT_ACCOUNT" ]; then
        log_info "Switching back to original account: $original_account"
        switch_account "$original_account" || true
    fi

    if [ $approval_count -eq 0 ]; then
        log_error "Failed to approve from any account"
        exit 1
    fi

    log_success "Approved by $approval_count account(s)"
    echo ""

    # Step 3: Wait for CI checks
    log_info "Step 3: Waiting for CI checks to pass"
    if ! wait_for_checks "$pr_number"; then
        log_error "CI checks failed or timed out"
        exit 1
    fi
    echo ""

    # Step 4: Wait for merge
    log_info "Step 4: Waiting for PR to be merged"
    if ! wait_for_merge "$pr_number"; then
        log_warning "PR was not auto-merged. Please check branch protection settings."
        exit 1
    fi
    echo ""

    # Step 5: Wait for release (optional)
    if [ "$skip_release_wait" != "--skip-release-wait" ]; then
        log_info "Step 5: Waiting for release workflow"
        if wait_for_release "$pr_number"; then
            echo ""
            log_success "=========================================="
            log_success "PR #$pr_number: All steps completed!"
            log_success "=========================================="
            echo ""
        else
            log_warning "Release workflow did not complete as expected"
            log_info "You may need to check the workflow manually"
            exit 1
        fi
    else
        log_info "Step 5: Skipping release workflow wait (--skip-release-wait)"
        echo ""
        log_success "=========================================="
        log_success "PR #$pr_number: Approved and merged!"
        log_success "=========================================="
        echo ""
    fi

    # Summary
    log_info "Summary:"
    gh pr view "$pr_number" --repo "$REPO"
}

# Script entry point
if [ $# -lt 1 ]; then
    echo "Usage: $0 PR_NUMBER [--skip-release-wait]"
    echo ""
    echo "Options:"
    echo "  --skip-release-wait    Skip waiting for release workflow to complete"
    echo ""
    echo "Examples:"
    echo "  $0 123                 # Approve PR #123 and wait for release"
    echo "  $0 123 --skip-release-wait  # Approve PR #123 but don't wait for release"
    exit 1
fi

main "$@"
