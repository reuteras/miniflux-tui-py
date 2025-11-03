#!/usr/bin/env python3
"""
miniflux-tui-py release utilities.

This script now supports two complementary flows:

1. `prepare` (default):
    - Runs quality gates on the current `main`.
    - Bumps the version and updates the changelog.
    - Creates a dedicated release branch with the changes.
    - Pushes the branch so you can open a pull request.

2. `tag`:
    - Validates that `main` is clean and in sync with `origin/main`.
    - Creates an annotated git tag (vX.Y.Z) for the current version.
    - Pushes the tag, which triggers the publish workflow.

    This sub-command is retained as a manual fallback. The preferred path is to run
    the `create-signed-tag` GitHub workflow so that the tag is GPG-signed in CI.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


class Colors:
    """ANSI color codes."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{'━' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'━' * 70}{Colors.NC}\n")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗{Colors.NC} {text}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.YELLOW}[i]{Colors.NC} {text}")


BRANCH_PROTECTION_PATTERNS = [
    "changes must be made through a pull request",
    "protected branch update failed",
    "protected branch hook declined",
    "bypassed rule violations",
]


def _print_command_output(stdout: str | None, stderr: str | None) -> None:
    """Print captured stdout/stderr from a successful command when requested."""
    if stdout:
        print(stdout, end="")
    if stderr:
        print(stderr, end="")


def _print_failure_output(
    error: subprocess.CalledProcessError,
    show_output: bool,
) -> None:
    """Print stdout/stderr from a failed command based on configuration."""
    if show_output:
        if error.stdout:
            print(error.stdout, end="")
        if error.stderr:
            print(error.stderr, end="")
    elif error.stderr:
        print(f"  {error.stderr}")


def _has_forbidden_pattern(
    stdout: str | None,
    stderr: str | None,
    forbidden_patterns: list[str],
) -> bool:
    """Return True if any forbidden pattern is present in command output."""
    combined_output = f"{stdout or ''}\n{stderr or ''}".lower()
    return any(pattern.lower() in combined_output for pattern in forbidden_patterns)


def run_command(
    cmd: list[str],
    description: str = "",
    show_output: bool = False,
    forbidden_patterns: list[str] | None = None,
) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        if show_output:
            _print_command_output(result.stdout, result.stderr)
        if forbidden_patterns and _has_forbidden_pattern(result.stdout, result.stderr, forbidden_patterns):
            if description:
                print_error(f"{description} blocked by repository rules")
            else:
                print_error("Command blocked by repository rules")
            return False
        return True
    except subprocess.CalledProcessError as error:
        if description:
            print_error(f"{description} failed")
        _print_failure_output(error, show_output)
        return False


def get_current_branch() -> str:
    """Return the current git branch."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        print_error("Could not determine current branch. Are you inside a git repository?")
        sys.exit(1)
    return result.stdout.strip()


def ensure_current_branch(expected: str) -> None:
    """Ensure we are on the expected branch."""
    branch = get_current_branch()
    if branch != expected:
        print_error(f"Releases must start from the '{expected}' branch (found '{branch}').")
        sys.exit(1)


def get_git_rev(ref: str) -> str:
    """Return the commit SHA for a ref."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", ref],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        print_error(f"Could not resolve git reference '{ref}'.")
        sys.exit(1)
    return result.stdout.strip()


def ensure_branch_synced(branch: str) -> None:
    """Ensure local branch matches origin/branch."""
    if not run_command(["git", "fetch", "origin", branch], f"Fetch origin/{branch}"):
        sys.exit(1)

    local_rev = get_git_rev("HEAD")
    remote_rev = get_git_rev(f"origin/{branch}")
    if local_rev != remote_rev:
        print_error(f"Local '{branch}' is not in sync with 'origin/{branch}'.")
        print_info(f"Run 'git pull --rebase origin {branch}' and retry.")
        sys.exit(1)


def branch_exists(branch: str) -> bool:
    """Return True if a local branch exists."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def remote_branch_exists(branch: str) -> bool:
    """Return True if the branch exists on origin."""
    result = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def ensure_branch_available(branch: str) -> None:
    """Ensure the release branch does not already exist."""
    if branch_exists(branch):
        print_error(f"Branch '{branch}' already exists locally.")
        sys.exit(1)

    if remote_branch_exists(branch):
        print_error(f"Branch '{branch}' already exists on origin.")
        sys.exit(1)


def tag_exists(tag: str) -> bool:
    """Return True if an annotated tag exists."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", tag],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    toml_path = Path("pyproject.toml")
    if not toml_path.exists():
        print_error("pyproject.toml not found")
        sys.exit(1)

    content = toml_path.read_text()
    match = re.search(r'version = "([0-9.]+)"', content)
    if not match:
        print_error("Could not find version in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def validate_version(version: str) -> bool:
    """Validate semantic versioning format."""
    return bool(re.match(r"^\d+\.\d+\.\d+$", version))


def suggest_next_version(current_version: str) -> str:
    """Suggest the next patch version based on current version."""
    parts = current_version.split(".")
    if len(parts) != 3:
        return current_version

    try:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        return f"{major}.{minor}.{patch + 1}"
    except ValueError:
        return current_version


def check_git_status() -> bool:
    """Check if git working directory is clean."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError:
        return False


def ensure_clean_working_tree() -> None:
    """Ensure there are no local modifications."""
    if not check_git_status():
        print_error("Working directory is not clean. Please commit or stash changes first.")
        sys.exit(1)


def update_version(new_version: str) -> bool:
    """Update version in pyproject.toml."""
    toml_path = Path("pyproject.toml")
    content = toml_path.read_text()
    current_version = get_current_version()

    new_content = re.sub(
        f'version = "{re.escape(current_version)}"',
        f'version = "{new_version}"',
        content,
    )

    if new_content == content:
        return False

    toml_path.write_text(new_content)
    return True


def get_previous_tag() -> str | None:
    """Get the most recent git tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def check_git_cliff_installed() -> bool:
    """Check if git-cliff is installed and available."""
    try:
        result = subprocess.run(
            ["git-cliff", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def generate_changelog_entry(new_version: str) -> str:
    """Generate changelog entry using git-cliff."""
    previous_tag = get_previous_tag()

    # Check if git-cliff is installed
    if not check_git_cliff_installed():
        print_error("git-cliff is not installed and is required for releases.")
        print_info("Install git-cliff before running the release script:")
        print_info("  - Via cargo: cargo install git-cliff")
        print_info("  - Via Homebrew (macOS): brew install git-cliff")
        print_info("  - Via package manager: See https://git-cliff.org/docs/installation")
        sys.exit(1)

    # Use git-cliff to generate the changelog
    try:
        # Determine the range to generate changelog for
        git_range = f"{previous_tag}..HEAD" if previous_tag else "HEAD"

        # Run git-cliff with our configuration
        result = subprocess.run(
            [
                "git-cliff",
                "--config",
                "cliff.toml",
                "--tag",
                new_version,
                git_range,
                "--unreleased",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Extract just the new version section from the output
        changelog_output = result.stdout
        # Remove the header (everything before the first "##")
        lines = changelog_output.split("\n")
        version_lines = []
        in_version_section = False

        for line in lines:
            if line.startswith((f"## [{new_version}]", f"## [v{new_version}]")):
                in_version_section = True
            elif line.startswith("## [") and in_version_section:
                # Stop at the next version section
                break

            if in_version_section:
                version_lines.append(line)

        return "\n".join(version_lines).strip()

    except subprocess.CalledProcessError as error:
        print_error(f"git-cliff failed: {error.stderr}")
        sys.exit(1)


def edit_changelog(new_version: str) -> bool:  # noqa: PLR0911
    """Update CHANGELOG by auto-generating from commits using git-cliff."""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print_error("CHANGELOG.md not found")
        return False

    print_info("Generating changelog entry from commits...")
    changelog_entry = generate_changelog_entry(new_version)
    print("\n" + "=" * 70)
    print(changelog_entry)
    print("=" * 70 + "\n")

    current_content = changelog_path.read_text()

    lines = current_content.split("\n")
    insert_pos = 0
    for idx, line in enumerate(lines):
        if line.startswith("# Changelog"):
            insert_pos = idx + 1
            break

    while insert_pos < len(lines) and lines[insert_pos].startswith("#"):
        insert_pos += 1
    if insert_pos < len(lines) and not lines[insert_pos].strip():
        insert_pos += 1

    lines.insert(insert_pos, "")
    for entry_line in reversed(changelog_entry.split("\n")):
        lines.insert(insert_pos, entry_line)

    changelog_path.write_text("\n".join(lines))
    print_success("Changelog updated with auto-generated entry")

    print_info("Press Enter to skip editing, or type 'e' to edit in $EDITOR:")
    edit_response = input("Edit changelog? (e/Enter): ").strip().lower()

    if edit_response != "e":
        content = changelog_path.read_text()
        if f"[{new_version}]" not in content:
            print_error("CHANGELOG.md was not updated")
            return False
        return True

    editor = os.environ.get("EDITOR", "nano").strip()
    try:
        # nosec: B603 - Editor from EDITOR env var is intentional and expected to be safe
        subprocess.run([editor, str(changelog_path)], check=True)
    except FileNotFoundError:
        print_error(f"Editor '{editor}' not found. Set $EDITOR environment variable.")
        print_info("Please edit CHANGELOG.md manually and run this script again.")
        return False
    except Exception as exc:
        print_error(f"Could not open editor: {exc}")
        print_info("Please edit CHANGELOG.md manually and run this script again.")
        return False

    content = changelog_path.read_text()
    if f"[{new_version}]" not in content:
        print_error("CHANGELOG.md was not updated")
        return False

    return True


def changelog_contains_version(version: str) -> bool:
    """Return True if the changelog references the version."""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        return False
    return f"[{version}]" in changelog_path.read_text()


def run_pre_release_checks() -> None:
    """Run tests, linting, and type checking before preparing the release."""
    print_header("Pre-Release Checks")

    print_info("Running tests...")
    if not run_command(
        ["uv", "run", "pytest", "tests", "--cov=miniflux_tui", "-q"],
        "Tests",
    ):
        print_error("Tests failed. Fix issues before preparing the release.")
        sys.exit(1)
    print_success("All tests passed")

    print_info("Running ruff linting...")
    if not run_command(
        ["uv", "run", "ruff", "check", "miniflux_tui", "tests"],
        "Linting",
    ):
        print_error("Linting failed. Run 'uv run ruff check miniflux_tui tests' to see issues.")
        sys.exit(1)
    print_success("Linting passed")

    print_info("Running type checking...")
    if not run_command(
        ["uv", "run", "pyright", "miniflux_tui", "tests"],
        "Type checking",
    ):
        print_error("Type checking failed. Run 'uv run pyright miniflux_tui tests' to see issues.")
        sys.exit(1)
    print_success("Type checking passed")


def update_release_files(current_version: str, new_version: str) -> None:
    """Update version and changelog for the release."""
    print_info("Updating version in pyproject.toml...")
    if not update_version(new_version):
        print_error("Could not update version in pyproject.toml")
        sys.exit(1)
    print_success(f"Version updated: {current_version} → {new_version}")

    print_info("Regenerating uv.lock to capture the new version...")
    if not run_command(["uv", "lock"], "Regenerate uv.lock", show_output=True):
        print_error("Failed to regenerate uv.lock; reverting version change.")
        update_version(current_version)
        sys.exit(1)
    print_success("uv.lock updated")

    print_header("Edit CHANGELOG")
    if not edit_changelog(new_version):
        update_version(current_version)
        sys.exit(1)
    print_success(f"CHANGELOG updated with version {new_version}")


def create_release_commit(new_version: str) -> None:
    """Stage and commit release artifacts."""
    if not run_command(
        ["git", "add", "pyproject.toml", "CHANGELOG.md", "uv.lock"],
        "Stage release files",
    ):
        print_error("Failed to stage release files.")
        sys.exit(1)
    print_success("Files staged for commit")

    commit_msg = f"chore: Release v{new_version}"
    if not run_command(["git", "commit", "-m", commit_msg], "Create release commit"):
        print_error("Failed to create release commit.")
        sys.exit(1)
    print_success(f"Commit created: {commit_msg}")


def push_release_branch(release_branch: str) -> None:
    """Push the release branch to origin."""
    print_info("Pushing release branch to origin...")
    if not run_command(
        ["git", "push", "-u", "origin", release_branch],
        "Push release branch",
        show_output=True,
        forbidden_patterns=BRANCH_PROTECTION_PATTERNS,
    ):
        print_error("Failed to push release branch. Resolve the issue and push manually.")
        sys.exit(1)
    print_success("Release branch pushed to origin")


def print_release_next_steps(new_version: str) -> None:
    """Display final instructions after preparing the release branch."""
    print_header("Release Branch Ready")

    print(f"{Colors.GREEN}✅ Release PR prepared successfully!{Colors.NC}\n")

    print(f"{Colors.RED}⚠️  CRITICAL: Follow ALL steps in order!{Colors.NC}\n")

    print(f"{Colors.YELLOW}Step 1: Create and Merge PR{Colors.NC}")
    print("   • Open a pull request from the release branch to main")
    print("   • Wait for CI to pass")
    print(f"   • {Colors.RED}MERGE THE PR{Colors.NC} (don't skip this!)")
    print()

    print(f"{Colors.YELLOW}Step 2: Update Local Main{Colors.NC}")
    print("   git checkout main")
    print("   git pull --ff-only")
    print()

    print(f"{Colors.YELLOW}Step 3: Verify Version on Main{Colors.NC}")
    print("   grep '^version' pyproject.toml")
    print(f'   # Should show: version = "{new_version}"')
    print()

    print(f"{Colors.YELLOW}Step 4: Push Tag to Trigger Publish{Colors.NC}")
    print("   # Option A: Manual tag push (recommended)")
    print(f'   git tag -s v{new_version} -m "v{new_version}"')
    print(f"   git push origin v{new_version}")
    print()
    print("   # Option B: Workflow + manual push")
    print(f"   gh workflow run create-signed-tag.yml --ref main --field version={new_version}")
    print(f"   sleep 30 && git fetch --tags && git push origin v{new_version}")
    print()

    print(f"{Colors.RED}⚠️  DO NOT create the tag before merging the PR!{Colors.NC}")
    print(f"{Colors.RED}   The build will use the wrong version from main!{Colors.NC}\n")

    print(f"{Colors.BLUE}📚 Full documentation: RELEASE.md{Colors.NC}")


def prepare_release() -> None:
    """Prepare a release branch with version and changelog updates."""
    print_header("miniflux-tui-py Release Preparation")

    ensure_current_branch("main")
    ensure_clean_working_tree()
    ensure_branch_synced("main")

    current_version = get_current_version()
    suggested_version = suggest_next_version(current_version)
    print_info(f"Current version: {current_version}")
    print(f"\n{Colors.YELLOW}Enter new version (default: {suggested_version}):{Colors.NC}")
    new_version = input("New version: ").strip()

    if not new_version:
        new_version = suggested_version

    if not validate_version(new_version):
        print_error("Invalid version format. Use semantic versioning (e.g., 0.2.1).")
        sys.exit(1)

    release_branch = f"release/v{new_version}"
    ensure_branch_available(release_branch)

    run_pre_release_checks()

    print_header("Creating Release Branch")

    if not run_command(["git", "switch", "-c", release_branch], "Create release branch"):
        sys.exit(1)
    print_success(f"Branch created: {release_branch}")

    update_release_files(current_version, new_version)
    create_release_commit(new_version)
    push_release_branch(release_branch)
    print_release_next_steps(new_version)


def create_release_tag(version_override: str | None) -> None:
    """Create and push an annotated tag for the current release (manual fallback path)."""
    print_header("miniflux-tui-py Tag Creation")
    print_info("Prefer running 'gh workflow run create-signed-tag.yml --ref main --field version=…' so the tag is signed in CI.")
    print_info("Continuing with manual tag creation using local credentials.")

    ensure_current_branch("main")
    ensure_clean_working_tree()
    ensure_branch_synced("main")

    version = version_override or get_current_version()
    if not validate_version(version):
        print_error("Invalid version format. Use semantic versioning (e.g., 0.2.1).")
        sys.exit(1)

    tag_name = f"v{version}"
    if tag_exists(tag_name):
        print_error(f"Tag '{tag_name}' already exists.")
        sys.exit(1)

    if not changelog_contains_version(version):
        print_info(f"Warning: CHANGELOG.md does not mention [{version}]. Proceed only if this is expected.")

    release_date = datetime.now(UTC).strftime("%Y-%m-%d")
    tag_message = f"Release v{version}\n\nPublished on {release_date}. See CHANGELOG.md for details."

    print_info(f"Creating tag {tag_name}...")
    if not run_command(["git", "tag", "-a", tag_name, "-m", tag_message], "Create tag"):
        sys.exit(1)
    print_success(f"Tag created: {tag_name}")

    print_info("Pushing tag to origin...")
    if not run_command(
        ["git", "push", "origin", tag_name],
        "Push tag",
        show_output=True,
    ):
        print_error("Failed to push tag. Resolve the issue and push manually.")
        sys.exit(1)
    print_success("Tag pushed to origin")

    print_header("Release Triggered")
    print("GitHub Actions will now:")
    print("  • Build and test the project")
    print("  • Publish artifacts to PyPI")
    print("  • Attach binaries and SBOMs to the GitHub release")
    print("")
    print("Monitor the workflow at https://github.com/reuteras/miniflux-tui-py/actions")
    print("PyPI will update once the publish job completes.")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Prepare release branches and create release tags for miniflux-tui-py.",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "prepare",
        help="Prepare a release branch (default action).",
    )

    tag_parser = subparsers.add_parser(
        "tag",
        help="Fallback: manually create and push the release tag after the PR merges.",
    )
    tag_parser.add_argument(
        "--version",
        help="Version to tag. Defaults to the version in pyproject.toml.",
        default=None,
    )

    args = parser.parse_args()
    if args.command is None:
        args.command = "prepare"
    return args


def main() -> None:
    """Entry point."""
    args = parse_args()

    if args.command == "prepare":
        prepare_release()
    elif args.command == "tag":
        create_release_tag(getattr(args, "version", None))
    else:
        print_error(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        print_error("Release cancelled by user")
        sys.exit(1)
    except Exception as exc:
        print_error(f"Unexpected error: {exc}")
        sys.exit(1)
