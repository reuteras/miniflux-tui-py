#!/bin/bash

# miniflux-tui-py Release Script
# Automates the release process: version bump, changelog, commit, tag, push

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if in git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

print_header "miniflux-tui-py Release Script"

# Get current version
current_version=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
print_info "Current version: $current_version"

# Prompt for new version
echo -e "${YELLOW}Enter new version (e.g., 0.2.1):${NC}"
read -p "New version: " new_version

# Validate version format (semantic versioning)
if ! [[ $new_version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format. Use semantic versioning (e.g., 0.2.1)"
    exit 1
fi

print_success "Version validated: $new_version"

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    print_error "Working directory is not clean. Please commit or stash changes first."
    git status
    exit 1
fi

print_header "Pre-Release Checks"

# Run tests
print_info "Running tests..."
if uv run pytest tests --cov=miniflux_tui -q > /dev/null 2>&1; then
    print_success "All tests passed"
else
    print_error "Tests failed. Fix issues before releasing."
    exit 1
fi

# Run linting
print_info "Running ruff linting..."
if uv run ruff check miniflux_tui tests > /dev/null 2>&1; then
    print_success "Linting passed"
else
    print_error "Linting failed. Run 'uv run ruff check miniflux_tui tests' to see issues."
    exit 1
fi

# Run type checking
print_info "Running type checking..."
if uv run pyright miniflux_tui tests > /dev/null 2>&1; then
    print_success "Type checking passed"
else
    print_error "Type checking failed. Run 'uv run pyright miniflux_tui tests' to see issues."
    exit 1
fi

print_header "Updating Files"

# Update version in pyproject.toml
print_info "Updating version in pyproject.toml..."
sed -i.bak "s/version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml
rm pyproject.toml.bak
print_success "Version updated: $current_version → $new_version"

# Open CHANGELOG for editing
print_header "Edit CHANGELOG"
print_info "Your CHANGELOG.md is now open for editing."
print_info "Add a new section at the top for version $new_version"
print_info "Example format:"
echo '
## ['"$new_version"'] - '"$(date +%Y-%m-%d)"'

### Added
- Feature description

### Changed
- Improvement description

### Fixed
- Bug fix description
'

$EDITOR CHANGELOG.md

# Verify CHANGELOG was updated
if grep -q "\[$new_version\]" CHANGELOG.md; then
    print_success "CHANGELOG updated with version $new_version"
else
    print_error "CHANGELOG not updated. Reverting changes."
    git checkout pyproject.toml
    exit 1
fi

print_header "Creating Release"

# Stage changes
git add pyproject.toml CHANGELOG.md
print_success "Files staged for commit"

# Commit
commit_msg="chore: Release v$new_version"
git commit -m "$(cat <<EOF
$commit_msg

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
print_success "Commit created: $commit_msg"

# Create git tag
tag_msg="Release v$new_version"
git tag -a "v$new_version" -m "$(cat <<EOF
$tag_msg

See CHANGELOG.md for detailed changes.
EOF
)"
print_success "Git tag created: v$new_version"

# Push changes and tag
print_info "Pushing changes and tag to origin..."
git push origin main
git push origin "v$new_version"
print_success "Changes and tag pushed to GitHub"

print_header "Release Complete! 🚀"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Version:      ${GREEN}v$new_version${NC}"
echo -e "Release Tag:  ${GREEN}v$new_version${NC}"
echo -e "GitHub:       ${GREEN}https://github.com/reuteras/miniflux-tui-py/releases/tag/v$new_version${NC}"
echo -e "PyPI:         ${GREEN}https://pypi.org/project/miniflux-tui-py/$new_version/${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${YELLOW}What happens next:${NC}"
echo "1. GitHub Actions will automatically:"
echo "   ✓ Run all tests"
echo "   ✓ Check linting and types"
echo "   ✓ Build distribution packages"
echo "   ✓ Publish to PyPI"
echo "   ✓ Create GitHub Release with artifacts"
echo ""
echo "2. Monitor the workflow at:"
echo "   https://github.com/reuteras/miniflux-tui-py/actions"
echo ""
echo "3. Check PyPI after publishing (usually within 1-2 minutes):"
echo "   https://pypi.org/project/miniflux-tui-py/"
echo ""
